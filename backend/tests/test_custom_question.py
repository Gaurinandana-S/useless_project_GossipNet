from tests.conftest import test_client as client

def test_custom_question_and_options():
    res = client.post('/api/game/create')
    assert res.status_code == 201
    g = res.json()
    gid = g['game_id']
    pid = g['visible_people'][0]['id']

    # 1. Test clicking predefined option key
    q1 = client.post(f'/api/game/{gid}/question', json={
        'person_id': pid,
        'question_key': 'household'
    })
    assert q1.status_code == 200
    d1 = q1.json()
    assert d1['question_key'] == 'household'
    assert 'persona_dialogue' in d1
    assert d1['questions_remaining'] == 9

    # 2. Test typing custom question in chatbox
    q2 = client.post(f'/api/game/{gid}/question', json={
        'person_id': pid,
        'custom_text': 'Who did you talk to recently?'
    })
    assert q2.status_code == 200
    d2 = q2.json()
    assert d2['question_key'] == 'talked_recently'
    assert d2['questions_remaining'] == 8
