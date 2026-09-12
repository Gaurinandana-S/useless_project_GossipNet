import random
import networkx as nx
from typing import Dict, Any, List
from app.services.kinship_service import (
    get_parents, get_children, get_spouses, get_siblings, get_relationship
)

CATEGORIZED_QUESTIONS = [
    # 1. BASIC INFORMATION
    {
        "key": "generation",
        "category": "BASIC",
        "text": "What generation are you from?",
        "description": "Asks about their age branch and place in the family tree."
    },
    {
        "key": "age",
        "category": "BASIC",
        "text": "How old are you?",
        "description": "Asks about their age."
    },
    {
        "key": "household",
        "category": "BASIC",
        "text": "Who lives in your household?",
        "description": "Reveals everyone residing in their home."
    },
    {
        "key": "relationship_with_person",
        "category": "BASIC",
        "text": "What is your role in the family?",
        "description": "Asks for basic kinship role overview."
    },
    {
        "key": "frequent_interactions",
        "category": "BASIC",
        "text": "Who do you frequently interact with?",
        "description": "Reveals social contacts, colleagues, and neighbors."
    },

    # 2. GOSSIP INVESTIGATION
    {
        "key": "previous_rumors",
        "category": "GOSSIP",
        "text": "Have you spread rumors before?",
        "description": "Probes their gossip reputation and past history."
    },
    {
        "key": "gossip_frequency",
        "category": "GOSSIP",
        "text": "How often do you pass on secrets?",
        "description": "Checks how frequently they share information."
    },
    {
        "key": "who_knows_everything",
        "category": "GOSSIP",
        "text": "Who in the family knows everything first?",
        "description": "Asks for their opinion on the main family news source."
    },
    {
        "key": "biggest_gossip",
        "category": "GOSSIP",
        "text": "Who is considered the biggest gossip?",
        "description": "Asks who has a reputation for leaking news."
    },
    {
        "key": "trustworthiness",
        "category": "GOSSIP",
        "text": "Do people trust the information you share?",
        "description": "Checks their credibility rating."
    },

    # 3. RELATIONSHIP INVESTIGATION
    {
        "key": "who_you_trust",
        "category": "RELATIONSHIP",
        "text": "Who do you trust most in the family?",
        "description": "Reveals close confidants and allies."
    },
    {
        "key": "who_annoys_you",
        "category": "RELATIONSHIP",
        "text": "Who causes the most family drama?",
        "description": "Identifies friction points and rivalries."
    },
    {
        "key": "never_tell_secret",
        "category": "RELATIONSHIP",
        "text": "Who would you never tell a secret to?",
        "description": "Reveals distrusted family members."
    },
    {
        "key": "who_you_avoid",
        "category": "RELATIONSHIP",
        "text": "Who do you usually avoid?",
        "description": "Reveals distant or strained connections."
    },

    # 4. DEDUCTION / CASE QUESTIONS
    {
        "key": "talked_recently",
        "category": "DEDUCTION",
        "text": "Who did you talk to recently?",
        "description": "Reveals recent communication links."
    },
    {
        "key": "visited_recently",
        "category": "DEDUCTION",
        "text": "Who visited your house recently?",
        "description": "Reveals household visitors."
    },
    {
        "key": "around_when_started",
        "category": "DEDUCTION",
        "text": "Who was around when this rumor started?",
        "description": "Probes proximity to the rumor origin."
    },
    {
        "key": "likely_to_spread",
        "category": "DEDUCTION",
        "text": "Who is most likely to spread something like this?",
        "description": "Asks for suspect leads."
    },
    # Phase 2 Propagation Questions
    {
        "key": "heard_rumor",
        "category": "DEDUCTION",
        "text": "Have you heard about this rumor?",
        "description": "Asks if this person has received the rumor."
    },
    {
        "key": "who_told_you",
        "category": "DEDUCTION",
        "text": "Who told you about the rumor?",
        "description": "Probes who passed the rumor to this person."
    },
    {
        "key": "who_you_told",
        "category": "DEDUCTION",
        "text": "Who have you already told?",
        "description": "Checks who received the rumor from this person."
    },
    {
        "key": "who_hears_last",
        "category": "DEDUCTION",
        "text": "Who in the family usually hears things last?",
        "description": "Asks for clues on who is out of the loop."
    },
    {
        "key": "daily_communication",
        "category": "DEDUCTION",
        "text": "Who do you speak to every single day?",
        "description": "Reveals high-frequency communication partners."
    }
]

DEAD_END_COMMENTARIES = [
    "❌ WRONG BRO. You learned something. Unfortunately, we're not sure what.",
    "CLUE ACQUIRED. Relevance: questionable.",
    "Excellent investigation. You are now suspicious of 4 additional people.",
    "You found another branch of the family. This was probably a mistake.",
    "Fascinating detail. The rumor mill continues uninterrupted.",
    "The family member nodded convincingly. Your investigation is equally confused."
]

def match_custom_question_key(custom_text: str) -> str:
    """Matches typed natural language question to the best question_key intent."""
    text = custom_text.lower()
    
    if any(w in text for w in ["live", "house", "home", "reside", "roommate", "household"]):
        return "household"
    elif any(w in text for w in ["talk", "speak", "call", "recent", "contact", "chat"]):
        return "talked_recently"
    elif any(w in text for w in ["visit", "visitor", "came", "come"]):
        return "visited_recently"
    elif any(w in text for w in ["rumor", "gossip", "secret", "leak", "spread"]):
        return "previous_rumors"
    elif any(w in text for w in ["trust", "believe", "friend", "ally"]):
        return "who_you_trust"
    elif any(w in text for w in ["annoy", "avoid", "hate", "enemy", "drama", "bother"]):
        return "who_annoys_you"
    elif any(w in text for w in ["age", "old", "years"]):
        return "age"
    elif any(w in text for w in ["gen", "generation", "elder", "branch"]):
        return "generation"
    elif any(w in text for w in ["who told", "heard from", "source"]):
        return "who_told_you"
    elif any(w in text for w in ["heard", "hear", "listen", "know about"]):
        return "heard_rumor"
    elif any(w in text for w in ["last", "who hears last", "end", "late", "out of loop"]):
        return "who_hears_last"
    elif any(w in text for w in ["daily", "every day", "always talk"]):
        return "daily_communication"
    else:
        return "frequent_interactions"


def evaluate_question(
    graph: nx.DiGraph,
    person_id: str,
    question_key: str,
    subject_id: str,
    custom_text: str = None,
    propagation_log: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates a chat interrogation question against persona traits and NetworkX graph.
    Supports predefined question_key or custom_text typed in the chat input.
    """
    if custom_text and not question_key:
        question_key = match_custom_question_key(custom_text)
    if not graph.has_node(person_id):
        return {
            "answer_text": "I have nothing to say.",
            "persona_dialogue": "I don't even know who I am.",
            "system_commentary": "❌ Unknown person.",
            "newly_revealed_person_ids": [],
            "newly_revealed_edges": []
        }

    p_data = graph.nodes[person_id]
    p_name = p_data.get("name", "Person")
    subj_name = graph.nodes[subject_id]["name"] if graph.has_node(subject_id) else "Subject"

    rng = random.Random()
    newly_revealed_ids = set()
    newly_edges = []
    
    def add_edge_info(u, v, rel_type):
        newly_edges.append({
            "id": f"e_{u}_{v}",
            "source": u,
            "target": v,
            "relationship_type": rel_type,
            "is_newly_discovered": True
        })

    persona_dialogue = ""

    # 1. BASIC INFORMATION
    if question_key == "generation":
        gen = p_data.get("generation", 2)
        if gen == 1:
            persona_dialogue = f'"I am from the founding generation of this family! Youngsters these days have no patience."'
        elif gen == 2:
            persona_dialogue = f'"I belong to Generation {gen}. I manage the household responsibilities while keeping an eye on everyone."'
        else:
            persona_dialogue = f'"I\'m Generation {gen}. We mostly try to stay out of the elders\' endless drama."'

    elif question_key == "age":
        age = p_data.get("age", 30)
        persona_dialogue = f'"I am {age} years old. Old enough to know who is lying in this house."'

    elif question_key == "household":
        h_id = p_data.get("household_id")
        housemates = [p for p, d in graph.nodes(data=True) if d.get("household_id") == h_id and p != person_id]
        if housemates:
            hm_names = [graph.nodes[h]["name"] for h in housemates]
            persona_dialogue = f'"In our house ({p_data.get("household_name", "House")}), I live with {", ".join(hm_names)}. Someone is always whispering in the kitchen."'
            for h in housemates:
                newly_revealed_ids.add(h)
                rel = get_relationship(graph, h, person_id)
                add_edge_info(person_id, h, rel)
        else:
            persona_dialogue = f'"I live alone in my household. Peace and quiet, except when relatives barge in."'

    elif question_key == "relationship_with_person":
        rel = get_relationship(graph, person_id, subject_id)
        persona_dialogue = f'"I am the {rel} of {subj_name}. Family ties are complicated around here."'
        if graph.has_node(subject_id):
            newly_revealed_ids.add(subject_id)
            add_edge_info(person_id, subject_id, rel)

    elif question_key == "frequent_interactions":
        socials = []
        for u, v, d in graph.edges(person_id, data=True):
            if d.get("primitive_type") in ["neighbor", "friend", "colleague"]:
                socials.append((v, d.get("primitive_type")))
        for u, v, d in graph.in_edges(person_id, data=True):
            if d.get("primitive_type") in ["neighbor", "friend", "colleague"]:
                socials.append((u, d.get("primitive_type")))
        if socials:
            soc_texts = [f"{graph.nodes[s[0]]['name']} ({s[1]})" for s in socials]
            persona_dialogue = f'"I frequently talk to {", ".join(soc_texts)}. News travels fast between us."'
            for s_id, s_type in socials:
                newly_revealed_ids.add(s_id)
                add_edge_info(person_id, s_id, s_type)
        else:
            persona_dialogue = f'"I keep to myself mostly, but neighbors are always watching."'

    # 2. GOSSIP INVESTIGATION
    elif question_key == "previous_rumors":
        rep = p_data.get("gossip_reputation", "MED")
        cnt = p_data.get("previous_rumor_count", 2)
        if rep == "HIGH":
            persona_dialogue = f'"Rumors? No! I simply make sure important information reaches the people who deserve it! (I may have mentioned {cnt} small stories before...)"'
        else:
            persona_dialogue = f'"Me? Spreading rumors? Absolutely not. I only repeat what is verified by at least three aunts."'

    elif question_key == "gossip_frequency":
        cnt = p_data.get("previous_rumor_count", 1)
        persona_dialogue = f'"I only talk when necessary. Though lately, there have been at least {cnt} major stories floating around."'

    elif question_key == "who_knows_everything":
        suspects = p_data.get("perceived_suspects", [])
        if suspects and graph.has_node(suspects[0]):
            lead_name = graph.nodes[suspects[0]]["name"]
            persona_dialogue = f'"If you ask me, {lead_name} always knows everything before the chai is even poured."'
            newly_revealed_ids.add(suspects[0])
            add_edge_info(person_id, suspects[0], "suspected informant")
        else:
            persona_dialogue = f'"Everyone in this family claims to know everything first!"'

    elif question_key == "biggest_gossip":
        rep = p_data.get("gossip_reputation", "MED")
        if rep == "HIGH":
            persona_dialogue = f'"Some jealous people point fingers at me, but I am merely a messenger of truth!"'
        else:
            persona_dialogue = f'"Check the older adults in Sector 1. They don\'t miss a single detail."'

    elif question_key == "trustworthiness":
        trust = p_data.get("trustworthiness", "MED")
        persona_dialogue = f'"My trustworthiness level is 100%! People come to me specifically because I keep things 100% confidential... usually."'

    # 3. RELATIONSHIP INVESTIGATION
    elif question_key == "who_you_trust":
        sibs = get_siblings(graph, person_id)
        spouses = get_spouses(graph, person_id)
        allies = sibs + spouses
        if allies:
            ally_names = [graph.nodes[a]["name"] for a in allies]
            persona_dialogue = f'"I trust {", ".join(ally_names)}. In this family, you can only rely on your immediate branch."'
            for a in allies:
                newly_revealed_ids.add(a)
                rel = get_relationship(graph, a, person_id)
                add_edge_info(person_id, a, rel)
        else:
            persona_dialogue = f'"Trust is earned. I trust very few people here."'

    elif question_key == "who_annoys_you":
        drama = p_data.get("drama_level", "MED")
        persona_dialogue = f'"Family drama level is {drama}! Everyone is constantly interfering in everyone else\'s business."'

    elif question_key == "never_tell_secret":
        suspects = p_data.get("perceived_suspects", [])
        if suspects and graph.has_node(suspects[0]):
            bad_name = graph.nodes[suspects[0]]["name"]
            persona_dialogue = f'"I would NEVER tell a secret to {bad_name}! It would be all over town in 5 minutes."'
            newly_revealed_ids.add(suspects[0])
            add_edge_info(person_id, suspects[0], "distrusted")
        else:
            persona_dialogue = f'"I wouldn\'t tell a secret to anyone who attends Sunday dinner."'

    elif question_key == "who_you_avoid":
        parents = get_parents(graph, person_id)
        if parents:
            p_names = [graph.nodes[p]["name"] for p in parents]
            persona_dialogue = f'"I try to avoid strict lectures from {", ".join(p_names)} whenever possible."'
            for p in parents:
                newly_revealed_ids.add(p)
                add_edge_info(p, person_id, "parent")
        else:
            persona_dialogue = f'"I avoid anyone carrying clipboard or asking questions... like you!"'

    # 4. DEDUCTION / CASE QUESTIONS
    elif question_key == "talked_recently":
        recent = p_data.get("recent_contacts", [])
        if recent:
            rc_names = [graph.nodes[r]["name"] for r in recent if graph.has_node(r)]
            persona_dialogue = f'"Recently? I was speaking with {", ".join(rc_names)}. We discussed ordinary matters."'
            for r in recent:
                if graph.has_node(r):
                    newly_revealed_ids.add(r)
                    add_edge_info(person_id, r, "recent contact")
        else:
            persona_dialogue = f'"I haven\'t spoken to anyone since yesterday morning."'

    elif question_key == "visited_recently":
        visitors = p_data.get("house_visitors", [])
        if visitors:
            v_names = [graph.nodes[v]["name"] for v in visitors if graph.has_node(v)]
            persona_dialogue = f'"Lately, {", ".join(v_names)} stopped by our house for tea."'
            for v in visitors:
                if graph.has_node(v):
                    newly_revealed_ids.add(v)
                    add_edge_info(person_id, v, "house visitor")
        else:
            persona_dialogue = f'"Nobody visited recently. Or at least nobody who admitted it."'

    elif question_key == "around_when_started":
        rel = get_relationship(graph, person_id, subject_id)
        persona_dialogue = f'"I was in the household area. As {subj_name}\'s {rel}, I notice whenever someone starts whispering."'
        if graph.has_node(subject_id):
            newly_revealed_ids.add(subject_id)
            add_edge_info(person_id, subject_id, rel)

    elif question_key == "likely_to_spread":
        suspects = p_data.get("perceived_suspects", [])
        if suspects and graph.has_node(suspects[0]):
            s_name = graph.nodes[suspects[0]]["name"]
            persona_dialogue = f'"If you want my honest opinion, {s_name} is most likely to start something like this!"'
            newly_revealed_ids.add(suspects[0])
            add_edge_info(person_id, suspects[0], "suspected starter")
        else:
            persona_dialogue = f'"Honestly, half the family has a reason to spread news about {subj_name}!"'

    # Phase 2 Question Handlers
    elif question_key == "heard_rumor":
        has_heard = False
        hear_time = None
        if propagation_log:
            for ev in propagation_log:
                if ev.get("target_id") == person_id or ev.get("source_id") == person_id:
                    has_heard = True
                    hear_time = ev.get("time_str")
                    break
        if has_heard:
            persona_dialogue = f'"Yes! Someone whispered it to me around {hear_time or "noon"}. In this family, nothing stays secret for long."'
        else:
            persona_dialogue = f'"No! This is the first time I am hearing about it. Where did you hear such nonsense?"'

    elif question_key == "who_told_you":
        teller_id = None
        teller_name = None
        if propagation_log:
            for ev in propagation_log:
                if ev.get("target_id") == person_id:
                    teller_id = ev.get("source_id")
                    teller_name = ev.get("source_name")
                    break
        if teller_id and graph.has_node(teller_id):
            persona_dialogue = f'"I am pretty sure {teller_name} told me earlier today. They swore me to secrecy, of course."'
            newly_revealed_ids.add(teller_id)
            rel = get_relationship(graph, teller_id, person_id)
            add_edge_info(teller_id, person_id, "rumor source")
        else:
            persona_dialogue = f'"Nobody told me directly. I either don\'t know or I heard it from the wind."'

    elif question_key == "who_you_told":
        told_targets = []
        if propagation_log:
            for ev in propagation_log:
                if ev.get("source_id") == person_id:
                    told_targets.append((ev.get("target_id"), ev.get("target_name")))
        if told_targets:
            target_names = [t[1] for t in told_targets]
            persona_dialogue = f'"Well... I may have accidentally mentioned it to {", ".join(target_names)}. But only in confidence!"'
            for tid, tname in told_targets:
                if graph.has_node(tid):
                    newly_revealed_ids.add(tid)
                    rel = get_relationship(graph, person_id, tid)
                    add_edge_info(person_id, tid, "passed rumor to")
        else:
            persona_dialogue = f'"I have not told anyone! I am a vault when it comes to family matters."'

    elif question_key == "who_hears_last":
        # Clue points to low communication frequency or secret-keepers
        elders_or_distant = [p for p, d in graph.nodes(data=True) if d.get("communication_frequency") == "LOW" or d.get("generation") == 1]
        if elders_or_distant:
            candidate = rng.choice(elders_or_distant)
            c_name = graph.nodes[candidate]["name"]
            persona_dialogue = f'"Usually {c_name} or people who rarely answer phone calls hear family news last."'
            newly_revealed_ids.add(candidate)
            add_edge_info(person_id, candidate, "potential endpoint")
        else:
            persona_dialogue = f'"Whoever is out of the loop usually hears it days later."'

    elif question_key == "daily_communication":
        contacts = p_data.get("recent_contacts", [])
        if contacts:
            c_names = [graph.nodes[c]["name"] for c in contacts if graph.has_node(c)]
            persona_dialogue = f'"I speak to {", ".join(c_names)} every single day without fail."'
            for c in contacts:
                if graph.has_node(c):
                    newly_revealed_ids.add(c)
                    add_edge_info(person_id, c, "daily contact")
        else:
            persona_dialogue = f'"I don\'t talk to anyone every single day. Silence is peace."'

    else:
        persona_dialogue = f'"I have no comment on that."'

    system_commentary = rng.choice(DEAD_END_COMMENTARIES)
    q_meta = next((q for q in CATEGORIZED_QUESTIONS if q["key"] == question_key), {"text": custom_text or question_key})

    return {
        "question_key": question_key,
        "question_text": q_meta.get("text", custom_text or question_key),
        "answer_text": persona_dialogue,
        "persona_dialogue": persona_dialogue,
        "system_commentary": system_commentary,
        "newly_revealed_person_ids": list(newly_revealed_ids),
        "newly_revealed_edges": newly_edges
    }
