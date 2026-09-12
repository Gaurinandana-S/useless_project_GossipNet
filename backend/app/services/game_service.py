import random
import uuid
import networkx as nx
from typing import Dict, Any, List
from sqlalchemy.orm import Session

def generate_uuid():
    return str(uuid.uuid4())

from app.models.game import Game, Household, Person, Relationship, Rumor, GameEvent
from app.services.graph_generator import generate_family_graph
from app.services.kinship_service import get_relationship
from app.services.question_service import evaluate_question, CATEGORIZED_QUESTIONS
from app.services.rumor_service import generate_rumor
from app.services.scoring_service import calculate_score
from app.services.propagation_service import simulate_rumor_propagation

WRONG_GUESS_MESSAGES = [
    "❌ WRONG BRO.",
    "❌ Nope. Excellent confidence, though.",
    "❌ Wrong. That person was just standing there.",
    "❌ Absolutely not. The family is disappointed.",
    "❌ Wrong. The investigation continues... Unfortunately.",
    "❌ Wrong. Nice try, but the rumor mill spins elsewhere."
]

CORRECT_GUESS_MESSAGES = [
    "✅ YOU WERE RIGHT. Unfortunately... YOU WERE WRONG.",
    "✅ Correct. Suspiciously correct.",
    "✅ YOU SOLVED IT. We don't know how."
]

PHASE2_WRONG_GUESS_MESSAGES = [
    "❌ WRONG BRO. The rumor apparently had somewhere else to go.",
    "❌ Nope. That wasn't the final ear in the grapevine.",
    "❌ Wrong. They heard it, but someone heard it even later.",
    "❌ Incorrect. The gossip train kept rolling past them.",
    "❌ Wrong. The family whispers did not stop there."
]

PHASE2_CORRECT_GUESS_MESSAGES = [
    "✅ YOU WERE RIGHT. Unfortunately... The rumor stopped right here!",
    "✅ Correct. They were the very last person to hear the scandal.",
    "✅ YOU PREDICTED THE END. The propagation halted with them."
]

GIVE_UP_MESSAGES = [
    "You have chosen peace. The rumor wins.",
    "5 GUESSES. ZERO ANSWERS. You have made a brave decision.",
    "The graph contains many people. Giving up was statistically reasonable."
]

# Helper to reconstruct NetworkX graph from database records
def build_networkx_graph(game: Game, db: Session) -> nx.DiGraph:
    graph = nx.DiGraph()
    people = db.query(Person).filter(Person.game_id == game.id).all()
    households = {h.id: h.name for h in db.query(Household).filter(Household.game_id == game.id).all()}
    
    for p in people:
        graph.add_node(
            p.id,
            id=p.id,
            name=p.name,
            gender=p.gender,
            age=p.age,
            generation=p.generation,
            household_id=p.household_id,
            household_name=households.get(p.household_id, "House"),
            tree_level=p.tree_level or 0,
            is_social=bool(p.is_social),
            gossip_reputation=p.gossip_reputation or "MED",
            previous_rumor_count=p.previous_rumor_count or 0,
            trustworthiness=p.trustworthiness or "MED",
            communication_frequency=p.communication_frequency or "MED",
            secret_keeping=p.secret_keeping or "MED"
        )

    rels = db.query(Relationship).filter(Relationship.game_id == game.id).all()
    for r in rels:
        graph.add_edge(r.person_a_id, r.person_b_id, primitive_type=r.primitive_type)

    return graph


def create_game_session(db: Session, difficulty: int = 1, random_seed: int = None, game_mode: str = "GUESS_RUMOR_START") -> Game:
    """Generates and saves a new game round."""
    actual_seed = random_seed if random_seed is not None else random.randint(100000, 999999)
    gen_result = generate_family_graph(difficulty_level=difficulty, random_seed=actual_seed)
    
    game = Game(
        seed=actual_seed,
        difficulty=difficulty,
        player_type="DETECTIVE",
        game_mode=game_mode,
        status="ACTIVE",
        current_reveal_level=0,
        questions_remaining=10,
        guesses_remaining=5,
        score=1000,
        visible_nodes=gen_result["initial_visible_ids"],
        visible_edges=[],
        asked_questions=[],
        guesses_made=[],
        propagation_log=[]
    )
    db.add(game)
    db.flush()

    # Save Households
    hh_map = {}
    for h in gen_result["households"]:
        hh_id = generate_uuid()
        hh_obj = Household(
            id=hh_id,
            game_id=game.id,
            name=h["name"],
            address_location=h["address_location"]
        )
        db.add(hh_obj)
        hh_map[h["id"]] = hh_id

    # Save People
    p_map = {}
    for p in gen_result["people"]:
        p_id = generate_uuid()
        p_obj = Person(
            id=p_id,
            game_id=game.id,
            household_id=hh_map.get(p["household_id"]),
            name=p["name"],
            age=p["age"],
            gender=p["gender"],
            generation=p["generation"],
            tree_level=p.get("tree_level", 0),
            is_social=p.get("is_social", False),
            gossip_reputation=p.get("gossip_reputation", "MED"),
            previous_rumor_count=p.get("previous_rumor_count", 0),
            trustworthiness=p.get("trustworthiness", "MED"),
            communication_frequency=p.get("communication_frequency", "MED"),
            secret_keeping=p.get("secret_keeping", "MED")
        )
        db.add(p_obj)
        p_map[p["id"]] = p_id

    db.flush()

    # Map initial visible node IDs to DB person IDs
    db_visible_nodes = [p_map[old_id] for old_id in gen_result["initial_visible_ids"] if old_id in p_map]
    game.visible_nodes = db_visible_nodes

    # Save Relationships
    graph = gen_result["graph"]
    for u, v, d in graph.edges(data=True):
        if u in p_map and v in p_map:
            rel_obj = Relationship(
                game_id=game.id,
                person_a_id=p_map[u],
                person_b_id=p_map[v],
                primitive_type=d.get("primitive_type", "social")
            )
            db.add(rel_obj)

    # Save Rumor
    subject_db_id = p_map[gen_result["rumor_subject_id"]]
    starter_db_id = p_map[gen_result["rumor_starter_id"]]
    subject_person = db.get(Person, subject_db_id)
    
    rumor_text = generate_rumor(subject_name=subject_person.name, seed=actual_seed)

    # Phase 2 Propagation Simulation
    final_db_id = None
    if game_mode == "GUESS_RUMOR_END":
        prop_res = simulate_rumor_propagation(
            graph=gen_result["graph"],
            starter_id=gen_result["rumor_starter_id"],
            subject_id=gen_result["rumor_subject_id"],
            random_seed=actual_seed
        )
        final_db_id = p_map.get(prop_res["final_person_id"], starter_db_id)
        prop_events_db = []
        for ev in prop_res["propagation_tree"]:
            prop_events_db.append({
                "step": ev["step"],
                "source_id": p_map.get(ev["source_id"], ev["source_id"]),
                "source_name": ev["source_name"],
                "target_id": p_map.get(ev["target_id"], ev["target_id"]),
                "target_name": ev["target_name"],
                "time_str": ev["time_str"],
                "timestamp": ev["timestamp"],
                "relationship": ev["relationship"]
            })
        game.propagation_log = prop_events_db

    rumor_obj = Rumor(
        game_id=game.id,
        content=rumor_text,
        subject_id=subject_db_id,
        starter_id=starter_db_id,
        final_person_id=final_db_id
    )
    db.add(rumor_obj)

    # Initial Visible Edges calculation
    nx_graph = build_networkx_graph(game, db)
    vis_edges = []
    for u_id in db_visible_nodes:
        for v_id in db_visible_nodes:
            if u_id != v_id and nx_graph.has_edge(u_id, v_id):
                edge_d = nx_graph.get_edge_data(u_id, v_id)
                rel_type = get_relationship(nx_graph, u_id, v_id)
                vis_edges.append({
                    "id": f"e_{u_id}_{v_id}",
                    "source": u_id,
                    "target": v_id,
                    "relationship_type": rel_type,
                    "is_newly_discovered": False
                })
    game.visible_edges = vis_edges

    # Event Logging
    evt = GameEvent(game_id=game.id, event_type="GAME_CREATED", details={"seed": actual_seed, "difficulty": difficulty, "game_mode": game_mode})
    db.add(evt)

    db.commit()
    db.refresh(game)
    return game


def serialize_game_state(game: Game, db: Session) -> Dict[str, Any]:
    """
    Constructs GameResponse payload, guaranteeing API security:
    starter_id is ONLY populated when status is 'SOLVED' or 'GAVE_UP'.
    final_person_id is ONLY populated when status is 'SOLVED' or 'GAVE_UP'.
    """
    people = db.query(Person).filter(Person.game_id == game.id).all()
    households = db.query(Household).filter(Household.game_id == game.id).all()
    rumor = db.query(Rumor).filter(Rumor.game_id == game.id).first()
    
    subject = db.get(Person, rumor.subject_id)
    starter = db.get(Person, rumor.starter_id)
    final_person = db.get(Person, rumor.final_person_id) if (rumor and rumor.final_person_id) else None

    hh_dict = {h.id: h.name for h in households}
    
    visible_node_set = set(game.visible_nodes or [])
    visible_people_list = []
    
    for p in people:
        if p.id in visible_node_set:
            visible_people_list.append({
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "gender": p.gender,
                "household_id": p.household_id,
                "household_name": hh_dict.get(p.household_id, "House"),
                "generation": p.generation,
                "tree_level": p.tree_level or 0,
                "is_social": bool(p.is_social),
                "gossip_reputation": p.gossip_reputation or "MED",
                "previous_rumor_count": p.previous_rumor_count or 0,
                "trustworthiness": p.trustworthiness or "MED",
                "communication_frequency": p.communication_frequency or "MED",
                "secret_keeping": p.secret_keeping or "MED"
            })

    # Sanitize rumor output based on game completion state
    is_completed = game.status in ["SOLVED", "GAVE_UP", "ROUND_COMPLETE"]
    
    rumor_payload = {
        "id": rumor.id,
        "content": rumor.content,
        "subject_id": subject.id,
        "subject_name": subject.name,
        "starter_id": starter.id if is_completed else None,
        "starter_name": starter.name if is_completed else None,
        "final_person_id": final_person.id if (is_completed and final_person) else None,
        "final_person_name": final_person.name if (is_completed and final_person) else None
    }

    starter_truth = None
    if is_completed and game.game_mode != "GUESS_RUMOR_END":
        starter_truth = {
            "starter_id": starter.id,
            "starter_name": starter.name,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "rumor_content": rumor.content
        }

    final_person_truth = None
    if is_completed and game.game_mode == "GUESS_RUMOR_END":
        final_person_truth = {
            "final_person_id": final_person.id if final_person else None,
            "final_person_name": final_person.name if final_person else "Unknown",
            "starter_id": starter.id,
            "starter_name": starter.name,
            "rumor_content": rumor.content,
            "propagation_tree": game.propagation_log or []
        }

    max_tree_level = max((p.tree_level for p in people if p.tree_level is not None), default=0)

    return {
        "game_id": game.id,
        "seed": game.seed,
        "difficulty": game.difficulty,
        "player_type": game.player_type,
        "game_mode": game.game_mode,
        "status": game.status,
        "current_reveal_level": game.current_reveal_level or 0,
        "max_tree_level": max_tree_level,
        "guess_count": game.guess_count or 0,
        "give_up_available": bool(game.give_up_available or ((game.guess_count or 0) > 0)),
        "questions_remaining": game.questions_remaining,
        "guesses_remaining": game.guesses_remaining,
        "score": game.score,
        "total_people_count": len(people),
        "visible_people_count": len(visible_people_list),
        "rumor": rumor_payload,
        "visible_people": visible_people_list,
        "visible_edges": game.visible_edges or [],
        "households": [{"id": h.id, "name": h.name, "address_location": h.address_location} for h in households],
        "available_questions": CATEGORIZED_QUESTIONS,
        "asked_questions": game.asked_questions or [],
        "guesses_made": game.guesses_made or [],
        "starter_truth": starter_truth,
        "final_person_truth": final_person_truth,
        "propagation_tree": game.propagation_log if is_completed else []
    }


def process_question(db: Session, game_id: str, person_id: str, question_key: str = None, custom_text: str = None) -> Dict[str, Any]:
    game = db.get(Game, game_id)
    if not game:
        raise ValueError("Game not found")
    
    if game.status != "ACTIVE":
        raise ValueError("Game is not active")

    if game.questions_remaining <= 0:
        raise ValueError("No investigation questions remaining")

    nx_graph = build_networkx_graph(game, db)
    rumor = db.query(Rumor).filter(Rumor.game_id == game.id).first()

    eval_result = evaluate_question(
        graph=nx_graph,
        person_id=person_id,
        question_key=question_key,
        subject_id=rumor.subject_id,
        custom_text=custom_text,
        propagation_log=game.propagation_log
    )

    # Decrement question counter
    game.questions_remaining -= 1
    questions_asked_count = 10 - game.questions_remaining
    wrong_guesses_count = game.guess_count or 0
    
    # Recalculate score
    game.score = calculate_score(
        questions_asked=questions_asked_count,
        wrong_guesses=wrong_guesses_count,
        is_solved=(game.status == "SOLVED"),
        gave_up=(game.status == "GAVE_UP"),
        guesses_remaining=game.guesses_remaining,
        difficulty=game.difficulty
    )

    # Questions DO NOT expand the family tree downward.
    # Only reveal side horizontal social contacts if explicitly returned by eval_result
    current_visible_nodes = set(game.visible_nodes or [])
    newly_added_nodes = []

    for new_id in eval_result.get("newly_revealed_person_ids", []):
        if new_id not in current_visible_nodes:
            current_visible_nodes.add(new_id)
            newly_added_nodes.append(new_id)
            
    game.visible_nodes = list(current_visible_nodes)

    # Update visible edges
    current_edges = list(game.visible_edges or [])
    existing_edge_ids = {e["id"] for e in current_edges}

    for edge in eval_result.get("newly_revealed_edges", []):
        if edge["id"] not in existing_edge_ids:
            current_edges.append(edge)
            existing_edge_ids.add(edge["id"])

    game.visible_edges = current_edges

    # Record question in history
    q_history = list(game.asked_questions or [])
    person_obj = db.get(Person, person_id)
    final_q_key = eval_result.get("question_key") or question_key or "general"
    final_q_text = eval_result.get("question_text") or custom_text or final_q_key
    q_meta = next((q for q in CATEGORIZED_QUESTIONS if q["key"] == final_q_key), {"text": final_q_text, "category": "GENERAL"})
    
    q_history.append({
        "person_id": person_id,
        "person_name": person_obj.name,
        "question_key": final_q_key,
        "question_category": q_meta.get("category", "GENERAL"),
        "question_text": final_q_text,
        "answer_text": eval_result["answer_text"],
        "persona_dialogue": eval_result["persona_dialogue"],
        "system_commentary": eval_result["system_commentary"]
    })
    game.asked_questions = q_history

    # Event Logging
    evt = GameEvent(game_id=game.id, event_type="QUESTION_ASKED", details={"person_id": person_id, "question_key": final_q_key})
    db.add(evt)

    db.commit()
    db.refresh(game)

    return {
        "question_key": final_q_key,
        "question_text": final_q_text,
        "answer_text": eval_result["answer_text"],
        "persona_dialogue": eval_result["persona_dialogue"],
        "system_commentary": eval_result["system_commentary"],
        "newly_revealed_person_ids": newly_added_nodes,
        "newly_revealed_edges": eval_result["newly_revealed_edges"],
        "unlocked_level": None,
        "questions_remaining": game.questions_remaining,
        "game_status": game.status
    }


def process_guess(db: Session, game_id: str, person_id: str) -> Dict[str, Any]:
    game = db.get(Game, game_id)
    if not game:
        raise ValueError("Game not found")

    if game.status != "ACTIVE":
        raise ValueError("Game is not active")

    # Unlimited guessing: player can guess any number of times
    game.guess_count = (game.guess_count or 0) + 1
    game.give_up_available = True

    rumor = db.query(Rumor).filter(Rumor.game_id == game.id).first()
    is_phase2 = (game.game_mode == "GUESS_RUMOR_END")
    target_id = rumor.final_person_id if is_phase2 else rumor.starter_id
    is_correct = (person_id == target_id)

    starter_person = db.get(Person, rumor.starter_id)
    final_person = db.get(Person, rumor.final_person_id) if rumor.final_person_id else None
    guessed_person = db.get(Person, person_id)

    unlocked_level = None
    newly_added_nodes = []

    rng = random.Random()
    if is_correct:
        commentary = rng.choice(PHASE2_CORRECT_GUESS_MESSAGES if is_phase2 else CORRECT_GUESS_MESSAGES)
        game.status = "SOLVED"
    else:
        # Escalating humorous commentary for wrong guesses
        escalating_commentaries = [
            "❌ WRONG BRO. That was certainly a decision. The investigation continues...",
            "❌ STILL WRONG. But now you're suspicious of significantly more people.",
            "❌ INCORRECT. You just unlocked another layer of family chaos.",
            "❌ NOT EVEN CLOSE. The family tree just grew downwards. Enjoy.",
            "❌ WRONG AGAIN. At this rate, the entire district is related to this rumor.",
            "❌ NOPE. Another branch of the family has emerged to judge you.",
            "❌ COMPLETELY INCORRECT. Maybe Give Up, Bro is calling your name?"
        ]
        commentary_idx = min(game.guess_count - 1, len(escalating_commentaries) - 1)
        commentary = escalating_commentaries[commentary_idx]

        # Progressive Downward Family Tree Expansion on WRONG GUESS
        curr_level = game.current_reveal_level if game.current_reveal_level is not None else 0
        next_level = curr_level + 1
        all_people = db.query(Person).filter(Person.game_id == game.id).all()
        max_level = max((p.tree_level for p in all_people if p.tree_level is not None), default=0)

        current_visible_nodes = set(game.visible_nodes or [])

        if next_level <= max_level:
            next_level_nodes = [p for p in all_people if (p.tree_level or 0) == next_level and p.id not in current_visible_nodes]
            if next_level_nodes:
                for nln in next_level_nodes:
                    current_visible_nodes.add(nln.id)
                    newly_added_nodes.append(nln.id)
                game.current_reveal_level = next_level
                unlocked_level = next_level

        game.visible_nodes = list(current_visible_nodes)

        # Update visible edges
        current_edges = list(game.visible_edges or [])
        existing_edge_ids = {e["id"] for e in current_edges}
        nx_graph = build_networkx_graph(game, db)

        for u in current_visible_nodes:
            for v in current_visible_nodes:
                if u != v and nx_graph.has_edge(u, v):
                    edge_id = f"e_{u}_{v}"
                    if edge_id not in existing_edge_ids:
                        rel_type = get_relationship(nx_graph, u, v)
                        current_edges.append({
                            "id": edge_id,
                            "source": u,
                            "target": v,
                            "relationship_type": rel_type,
                            "is_newly_discovered": True
                        })
                        existing_edge_ids.add(edge_id)

    if not is_correct:
        game.guesses_remaining = max(0, game.guesses_remaining - 1)

    questions_asked_count = 10 - game.questions_remaining
    wrong_guesses_count = game.guess_count if not is_correct else max(0, game.guess_count - 1)

    game.score = calculate_score(
        questions_asked=questions_asked_count,
        wrong_guesses=wrong_guesses_count,
        is_solved=(game.status == "SOLVED"),
        gave_up=(game.status == "GAVE_UP"),
        guesses_remaining=game.guesses_remaining,
        difficulty=game.difficulty
    )

    guesses_log = list(game.guesses_made or [])
    guesses_log.append({
        "person_id": person_id,
        "person_name": guessed_person.name,
        "is_correct": is_correct,
        "commentary": commentary
    })
    game.guesses_made = guesses_log

    evt = GameEvent(game_id=game.id, event_type="GUESS_MADE", details={"guessed_person_id": person_id, "is_correct": is_correct, "game_mode": game.game_mode, "guess_count": game.guess_count})
    db.add(evt)

    db.commit()
    db.refresh(game)

    return {
        "is_correct": is_correct,
        "commentary": commentary,
        "guess_count": game.guess_count,
        "give_up_available": True,
        "guesses_remaining": game.guesses_remaining,
        "unlocked_level": unlocked_level,
        "newly_revealed_person_ids": newly_added_nodes,
        "game_status": game.status,
        "starter_id": starter_person.id if game.status in ["SOLVED", "GAVE_UP"] else None,
        "starter_name": starter_person.name if game.status in ["SOLVED", "GAVE_UP"] else None,
        "final_person_id": final_person.id if (final_person and game.status in ["SOLVED", "GAVE_UP"]) else None,
        "final_person_name": final_person.name if (final_person and game.status in ["SOLVED", "GAVE_UP"]) else None,
        "propagation_tree": game.propagation_log if game.status in ["SOLVED", "GAVE_UP"] else [],
        "final_score": game.score
    }


def process_give_up(db: Session, game_id: str) -> Dict[str, Any]:
    game = db.get(Game, game_id)
    if not game:
        raise ValueError("Game not found")

    if not game.give_up_available and (game.guess_count or 0) < 1:
        raise ValueError("Give Up is only available after making at least one guess")

    game.status = "GAVE_UP"
    
    questions_asked_count = 10 - game.questions_remaining
    wrong_guesses_count = game.guess_count or 0

    game.score = calculate_score(
        questions_asked=questions_asked_count,
        wrong_guesses=wrong_guesses_count,
        is_solved=False,
        gave_up=True,
        guesses_remaining=0,
        difficulty=game.difficulty
    )

    rumor = db.query(Rumor).filter(Rumor.game_id == game.id).first()
    starter = db.get(Person, rumor.starter_id)
    subject = db.get(Person, rumor.subject_id)
    final_person = db.get(Person, rumor.final_person_id) if rumor.final_person_id else None

    nx_graph = build_networkx_graph(game, db)
    path = []
    try:
        undirected = nx_graph.to_undirected()
        dest_id = rumor.final_person_id if (game.game_mode == "GUESS_RUMOR_END" and rumor.final_person_id) else rumor.subject_id
        raw_path = nx.shortest_path(undirected, rumor.starter_id, dest_id)
        path = [db.get(Person, node_id).name for node_id in raw_path]
    except Exception:
        dest_name = final_person.name if final_person else subject.name
        path = [starter.name, dest_name]

    rng = random.Random()
    commentary = rng.choice(GIVE_UP_MESSAGES)

    evt = GameEvent(game_id=game.id, event_type="GAVE_UP", details={"score": game.score, "game_mode": game.game_mode})
    db.add(evt)

    db.commit()
    db.refresh(game)

    return {
        "starter_id": starter.id,
        "starter_name": starter.name,
        "final_person_id": final_person.id if final_person else None,
        "final_person_name": final_person.name if final_person else None,
        "subject_id": subject.id,
        "subject_name": subject.name,
        "rumor_content": rumor.content,
        "relationship_path": path,
        "propagation_tree": game.propagation_log or [],
        "commentary": commentary,
        "final_score": game.score,
        "game_status": game.status
    }


def process_next_game(db: Session, current_game_id: str) -> Game:
    """
    Creates a COMPLETELY fresh game round with escalating difficulty and brand new graph.
    Preserves game_mode. Does NOT reuse existing graph structure.
    """
    current_game = db.get(Game, current_game_id)
    new_difficulty = current_game.difficulty + 1 if current_game else 1
    game_mode = current_game.game_mode if current_game else "GUESS_RUMOR_START"
    
    # Generate new random seed
    new_seed = random.randint(100000, 999999)
    if current_game and new_seed == current_game.seed:
        new_seed += 1

    return create_game_session(db=db, difficulty=new_difficulty, random_seed=new_seed, game_mode=game_mode)
