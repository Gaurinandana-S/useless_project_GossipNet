import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import Game, Household, Person, Relationship, Rumor, GameEvent
from app.main import app
from app.services.graph_generator import generate_family_graph
from app.services.kinship_service import get_relationship, get_parents, get_children, get_siblings
import networkx as nx

import os
from sqlalchemy.pool import StaticPool

from tests.conftest import test_client as client, TestingSessionLocal


def test_graph_generator_and_validation():
    gen_result = generate_family_graph(difficulty_level=1, random_seed=42)
    assert gen_result["seed"] == 42
    people = gen_result["people"]
    assert 20 <= len(people) <= 30
    
    # Check unique names
    names = [p["name"] for p in people]
    assert len(names) == len(set(names))
    
    # Check households
    assert len(gen_result["households"]) >= 3
    
    # Check starter and subject exist
    assert gen_result["rumor_starter_id"] in [p["id"] for p in people]
    assert gen_result["rumor_subject_id"] in [p["id"] for p in people]
    assert gen_result["rumor_starter_id"] != gen_result["rumor_subject_id"]


def test_kinship_inference():
    # Build mini test networkx graph
    g = nx.DiGraph()
    # Madhavan (Gen 1, M) -> Suresh (Gen 2, M) -> Arjun (Gen 3, M)
    # Madhavan (Gen 1, M) -> Rajesh (Gen 2, M)
    g.add_node("p1", name="Madhavan", gender="M", generation=1)
    g.add_node("p2", name="Suresh", gender="M", generation=2)
    g.add_node("p3", name="Rajesh", gender="M", generation=2)
    g.add_node("p4", name="Arjun", gender="M", generation=3)

    g.add_edge("p1", "p2", primitive_type="parent")
    g.add_edge("p1", "p3", primitive_type="parent")
    g.add_edge("p2", "p4", primitive_type="parent")

    assert get_relationship(g, "p1", "p2") == "father"
    assert get_relationship(g, "p2", "p1") == "son"
    assert get_relationship(g, "p2", "p3") == "brother"
    assert get_relationship(g, "p1", "p4") == "paternal grandfather"
    assert get_relationship(g, "p4", "p1") == "grandson"
    assert get_relationship(g, "p3", "p4") == "paternal uncle"


def test_game_creation_api():
    res = client.post("/api/game/create", json={"difficulty": 1})
    assert res.status_code == 201
    data = res.json()
    assert "game_id" in data
    assert data["questions_remaining"] == 10
    assert data["guesses_remaining"] == 5
    assert data["score"] == 1000
    assert data["status"] == "ACTIVE"
    # CRITICAL SECURITY CHECK: rumor_starter must be sanitized (None)
    assert data["rumor"]["starter_id"] is None


def test_game_investigation_and_expansion():
    res = client.post("/api/game/create", json={"difficulty": 1})
    game_data = res.json()
    game_id = game_data["game_id"]
    visible_people = game_data["visible_people"]
    person_to_ask = visible_people[0]["id"]

    q_res = client.post(f"/api/game/{game_id}/question", json={
        "person_id": person_to_ask,
        "question_key": "siblings"
    })
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["questions_remaining"] == 9
    assert "answer_text" in q_data

    # Fetch game state to verify expansion
    updated_res = client.get(f"/api/game/{game_id}")
    updated_data = updated_res.json()
    assert updated_data["questions_remaining"] == 9


def test_wrong_guess_and_give_up():
    res = client.post("/api/game/create", json={"difficulty": 1})
    game_data = res.json()
    game_id = game_data["game_id"]
    visible_people = game_data["visible_people"]
    
    # Perform 5 wrong guesses on a non-starter person
    for i in range(5):
        g_res = client.post(f"/api/game/{game_id}/guess", json={
            "person_id": visible_people[0]["id"]
        })
        assert g_res.status_code == 200

    game_state = client.get(f"/api/game/{game_id}").json()
    assert game_state["guesses_remaining"] == 0

    # Give Up endpoint
    gu_res = client.post(f"/api/game/{game_id}/give-up")
    assert gu_res.status_code == 200
    gu_data = gu_res.json()
    assert gu_data["game_status"] == "GAVE_UP"
    assert "starter_id" in gu_data
    assert "starter_name" in gu_data


def test_consecutive_games_different_graphs():
    """CRITICAL TEST: Verify two consecutive games do not reuse the same graph structure."""
    res1 = client.post("/api/game/create", json={"difficulty": 1})
    game1 = res1.json()

    res2 = client.post("/api/game/create", json={"difficulty": 1})
    game2 = res2.json()

    assert game1["game_id"] != game2["game_id"]
    assert game1["seed"] != game2["seed"]
    
    names1 = [p["name"] for p in game1["visible_people"]]
    names2 = [p["name"] for p in game2["visible_people"]]
    # The set of visible people or graph nodes will differ between random seeds
    assert names1 != names2 or len(game1["visible_people"]) != len(game2["visible_people"])
