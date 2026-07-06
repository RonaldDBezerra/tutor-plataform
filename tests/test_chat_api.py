from __future__ import annotations


def test_chat_flow(client, fake_services):
    tutor_response = client.post(
        "/api/v1/tutors",
        json={
            "name": "Chat Tutor",
            "description": "Friendly",
            "system_prompt": "You are a tutor.",
            "status": "ACTIVE",
        },
    )
    tutor_id = tutor_response.json()["id"]

    client.post(
        f"/api/v1/tutors/{tutor_id}/knowledge-sources",
        json={
            "provider_type": "HTTP_TEXT",
            "source_name": "Docs",
            "source_url": "https://example.com/docs",
            "configuration": {},
            "enabled": True,
        },
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "tutor_id": tutor_id,
            "question": "What can you teach me?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"]
    assert payload["answer"].startswith("Answer for Chat Tutor")
    assert len(payload["sources"]) == 1

    response = client.post(
        "/api/v1/chat",
        json={
            "tutor_id": tutor_id,
            "conversation_id": payload["conversation_id"],
            "question": "And now?",
        },
    )

    assert response.status_code == 200
    second_payload = response.json()
    assert second_payload["conversation_id"] == payload["conversation_id"]
    assert len(fake_services["chat_service"].conversations) == 1
    assert len(fake_services["chat_service"].messages) == 4
    assert len(fake_services["tutor_agent"].calls[-1]["history"]) == 2

    response = client.post(
        "/api/v1/embed/chat",
        json={
            "tutor_id": tutor_id,
            "conversation_id": second_payload["conversation_id"],
            "question": "And now?",
        },
    )

    assert response.status_code == 200
    assert response.json()["conversation_id"] == second_payload["conversation_id"]
