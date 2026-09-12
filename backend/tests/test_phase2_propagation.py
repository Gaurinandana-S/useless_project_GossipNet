import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import Game, Household, Person, Relationship, Rumor, GameEvent
from app.main import app
from app.services.graph_generator import generate_family_graph
from app.services.propagation_service import simulate_rumor_propagation

from tests.conftest import test_client as client, TestingSessionLocal


def test_propagation_service_unit():
    gen_result = generate_family_graph(difficulty_level=1, random_seed=42)
    prop_result = simulate_rumor_propagation(
        graph=gen_result["graph"],
        starter_id=gen_result["rumor_starter_id"],
        subject_id=gen_result["rumor_subject_id"],
        random_seed=42
    )

    assert "final_person_id" in prop_result
    assert "propagation_tree" in prop_result
    assert len(prop_result["reached_person_ids"]) >= 1
    assert prop_result["final_person_id"] in prop_result["reached_person_ids"]
    
    # Verify events structure
    events = prop_result["propagation_tree"]
    if events:
        for idx, ev in enumerate(events):
            assert ev["step"] == idx + 1
            assert "source_id" in ev
            assert "target_id" in ev
            assert "time_str" in ev
            assert "relationship" in ev


def test_phase2_create_game_and_sanitization():
    res = client.post("/api/game/create", json={"difficulty": 1, "random_seed": 777, "game_mode": "GUESS_RUMOR_END"})
    assert res.status_code == 201
    data = res.json()

    assert data["game_mode"] == "GUESS_RUMOR_END"
    assert data["status"] == "ACTIVE"
    assert data["questions_remaining"] == 10
    assert data["guesses_remaining"] == 5

    # CRITICAL: Starter and final person MUST be hidden during active gameplay
    assert data["rumor"]["starter_id"] is None
    assert data["rumor"]["starter_name"] is None
    assert data["rumor"]["final_person_id"] is None
    assert data["rumor"]["final_person_name"] is None
    assert data["starter_truth"] is None
    assert data["final_person_truth"] is None
    assert data["propagation_tree"] == []


def test_phase2_questions_and_persona_dialogue():
    res = client.post("/api/game/create", json={"difficulty": 1, "random_seed": 12345, "game_mode": "GUESS_RUMOR_END"})
    game_data = res.json()
    game_id = game_data["game_id"]
    person_id = game_data["visible_people"][0]["id"]

    # Ask Phase 2 specific question: heard_rumor
    q_res = client.post(f"/api/game/{game_id}/question", json={
        "person_id": person_id,
        "question_key": "heard_rumor"
    })
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["questions_remaining"] == 9
    assert len(q_data["answer_text"]) > 0
    assert len(q_data["persona_dialogue"]) > 0

    # Ask Phase 2 specific question: who_told_you
    q2_res = client.post(f"/api/game/{game_id}/question", json={
        "person_id": person_id,
        "question_key": "who_told_you"
    })
    assert q2_res.status_code == 200
    q2_data = q2_res.json()
    assert q2_data["questions_remaining"] == 8

    # Ask Phase 2 specific question: who_hears_last
    q3_res = client.post(f"/api/game/{game_id}/question", json={
        "person_id": person_id,
        "question_key": "who_hears_last"
    })
    assert q3_res.status_code == 200
    q3_data = q3_res.json()
    assert q3_data["questions_remaining"] == 7


def test_phase2_guess_wrong_and_correct():
    res = client.post("/api/game/create", json={"difficulty": 1, "random_seed": 999, "game_mode": "GUESS_RUMOR_END"})
    game_data = res.json()
    game_id = game_data["game_id"]

    db = TestingSessionLocal()
    rumor = db.query(Rumor).filter(Rumor.game_id == game_id).first()
    final_person_id = rumor.final_person_id
    starter_id = rumor.starter_id
    db.close()

    # Pick a wrong candidate
    wrong_candidate_id = starter_id if starter_id != final_person_id else game_data["visible_people"][0]["id"]
    if wrong_candidate_id == final_person_id:
        wrong_candidate_id = game_data["visible_people"][1]["id"]

    # Wrong guess
    guess_res = client.post(f"/api/game/{game_id}/guess", json={"person_id": wrong_candidate_id})
    assert guess_res.status_code == 200
    guess_data = guess_res.json()
    assert guess_data["is_correct"] is False
    assert guess_data["guesses_remaining"] == 4
    assert guess_data["game_status"] == "ACTIVE"

    # Correct guess with the real final_person_id
    correct_res = client.post(f"/api/game/{game_id}/guess", json={"person_id": final_person_id})
    assert correct_res.status_code == 200
    correct_data = correct_res.json()
    assert correct_data["is_correct"] is True
    assert correct_data["game_status"] == "SOLVED"
    assert correct_data["final_person_id"] == final_person_id
    assert len(correct_data["propagation_tree"]) >= 0

    # Retrieve game state when solved: final_person_truth and propagation_tree should be revealed
    final_state = client.get(f"/api/game/{game_id}").json()
    assert final_state["status"] == "SOLVED"
    assert final_state["rumor"]["final_person_id"] == final_person_id
    assert final_state["final_person_truth"] is not None
    assert final_state["final_person_truth"]["final_person_id"] == final_person_id


def test_phase1_backwards_compatibility():
    # Verify Phase 1 continues to work without regression
    res = client.post("/api/game/create", json={"difficulty": 1, "random_seed": 555, "game_mode": "GUESS_RUMOR_START"})
    assert res.status_code == 201
    game_data = res.json()
    assert game_data["game_mode"] == "GUESS_RUMOR_START"
    
    db = TestingSessionLocal()
    rumor = db.query(Rumor).filter(Rumor.game_id == game_data["game_id"]).first()
    starter_id = rumor.starter_id
    db.close()

    guess_res = client.post(f"/api/game/{game_data['game_id']}/guess", json={"person_id": starter_id})
    assert guess_res.status_code == 200
    assert guess_res.json()["is_correct"] is True
    assert guess_res.json()["game_status"] == "SOLVED"
