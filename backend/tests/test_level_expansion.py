import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_guess_triggered_tree_expansion():
    """Verify that guesses (not chat questions) trigger downward tree expansion and unlimited guesses are supported."""
    # 1. Create Game
    res = client.post("/api/game/create", json={"difficulty": 1, "game_mode": "GUESS_RUMOR_START"})
    assert res.status_code == 201
    game = res.json()
    game_id = game["game_id"]

    assert game["current_reveal_level"] == 0
    assert game["guess_count"] == 0
    assert game["give_up_available"] is False
    init_visible_count = game["visible_people_count"]

    # 2. Interrogate someone: verify questions DO NOT expand tree levels
    person_0_id = game["visible_people"][0]["id"]
    q1_res = client.post(f"/api/game/{game_id}/question", json={
        "person_id": person_0_id,
        "question_key": "generation"
    })
    assert q1_res.status_code == 200
    q1_data = q1_res.json()
    assert q1_data["unlocked_level"] is None

    # State still at level 0
    g_after_q = client.get(f"/api/game/{game_id}").json()
    assert g_after_q["current_reveal_level"] == 0
    assert g_after_q["visible_people_count"] == init_visible_count

    # 3. Submit Wrong Guess #1: triggers downward tree expansion to Level 1
    # We find someone who is NOT the starter to guarantee wrong guess
    starter_id = client.get(f"/api/game/{game_id}").json()["rumor"].get("starter_id") # Note: sanitized to None during game
    # Guess the first person (odds of being the starter are near zero since starter was chosen from gen 2/3)
    guess1_res = client.post(f"/api/game/{game_id}/guess", json={"person_id": person_0_id})
    assert guess1_res.status_code == 200
    guess1_data = guess1_res.json()
    
    assert guess1_data["guess_count"] == 1
    assert guess1_data["give_up_available"] is True
    assert guess1_data["unlocked_level"] == 1

    g_after_guess1 = client.get(f"/api/game/{game_id}").json()
    assert g_after_guess1["current_reveal_level"] == 1
    assert g_after_guess1["visible_people_count"] > init_visible_count
    assert g_after_guess1["give_up_available"] is True

    # 4. Unlimited Guessing: Test 6 consecutive wrong guesses without hitting a limit
    prev_visible = g_after_guess1["visible_people_count"]
    for i in range(2, 7):
        guess_res = client.post(f"/api/game/{game_id}/guess", json={"person_id": person_0_id})
        assert guess_res.status_code == 200
        g_data = guess_res.json()
        assert g_data["guess_count"] == i
        assert g_data["game_status"] == "ACTIVE"

    # 5. Give Up after guesses
    give_up_res = client.post(f"/api/game/{game_id}/give-up")
    assert give_up_res.status_code == 200
    assert give_up_res.json()["game_status"] == "GAVE_UP"
