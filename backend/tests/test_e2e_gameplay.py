import pytest
from tests.conftest import test_client as client

def test_full_e2e_gameplay_flow():
    """End-to-end verification of Phase 1 Detective gameplay loop."""
    # 1. Create Game (Round 1)
    res = client.post("/api/game/create", json={"difficulty": 1})
    assert res.status_code == 201
    game = res.json()
    game_id = game["game_id"]
    
    assert game["player_type"] == "DETECTIVE"
    assert game["game_mode"] == "GUESS_RUMOR_START"
    assert game["questions_remaining"] == 10
    assert game["guesses_remaining"] == 5
    assert game["score"] == 1000
    assert game["rumor"]["starter_id"] is None  # SANITIZED CHECK
    
    initial_visible_count = game["visible_people_count"]
    assert 5 <= initial_visible_count <= 10

    # 2. Ask Question (Investigate)
    person_id = game["visible_people"][0]["id"]
    q_res = client.post(f"/api/game/{game_id}/question", json={
        "person_id": person_id,
        "question_key": "siblings"
    })
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["questions_remaining"] == 9

    # 3. Fetch updated game state & verify graph expanded
    updated_res = client.get(f"/api/game/{game_id}")
    assert updated_res.status_code == 200
    updated_game = updated_res.json()
    assert updated_game["questions_remaining"] == 9

    # 4. Make Wrong Guesses until Guesses = 0
    for _ in range(5):
        g_res = client.post(f"/api/game/{game_id}/guess", json={
            "person_id": person_id
        })
        assert g_res.status_code == 200

    # 5. Verify Guesses = 0
    state_zero_guesses = client.get(f"/api/game/{game_id}").json()
    assert state_zero_guesses["guesses_remaining"] == 0

    # 6. Execute Give Up
    gu_res = client.post(f"/api/game/{game_id}/give-up")
    assert gu_res.status_code == 200
    gu_data = gu_res.json()
    assert gu_data["game_status"] == "GAVE_UP"
    assert gu_data["starter_name"] is not None
    assert gu_data["subject_name"] is not None

    # 7. Next Rumor (Create fresh round)
    next_res = client.post(f"/api/game/{game_id}/next")
    assert next_res.status_code == 200
    next_game = next_res.json()
    
    assert next_game["game_id"] != game_id
    assert next_game["difficulty"] == 2
    assert next_game["questions_remaining"] == 10
    assert next_game["guesses_remaining"] == 5
    assert next_game["rumor"]["starter_id"] is None
