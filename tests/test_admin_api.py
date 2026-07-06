from __future__ import annotations

from uuid import UUID

from app.models.enums import ProviderType, TutorStatus


def test_tutor_crud(client, fake_services):
    response = client.post(
        "/api/v1/tutors",
        json={
            "name": "Tutor One",
            "description": "A helper tutor",
            "system_prompt": "You are helpful.",
            "status": "ACTIVE",
        },
    )
    assert response.status_code == 201
    tutor = response.json()
    tutor_id = UUID(tutor["id"])

    response = client.get("/api/v1/tutors")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/api/v1/tutors/{tutor_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Tutor One"

    response = client.patch(
        f"/api/v1/tutors/{tutor_id}",
        json={"name": "Tutor Two", "status": "INACTIVE"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Tutor Two"
    assert response.json()["status"] == "INACTIVE"

    response = client.delete(f"/api/v1/tutors/{tutor_id}")
    assert response.status_code == 204
    assert fake_services["tutor_service"].tutors[tutor_id].status == TutorStatus.INACTIVE


def test_knowledge_source_crud(client, fake_services):
    tutor_response = client.post(
        "/api/v1/tutors",
        json={
            "name": "Tutor One",
            "description": None,
            "system_prompt": "Prompt",
            "status": "ACTIVE",
        },
    )
    tutor_id = tutor_response.json()["id"]

    response = client.post(
        f"/api/v1/tutors/{tutor_id}/knowledge-sources",
        json={
            "provider_type": "HTTP_TEXT",
            "source_name": "Docs",
            "source_url": "https://example.com/docs",
            "configuration": {"timeout": 3},
            "enabled": True,
        },
    )
    assert response.status_code == 201
    source = response.json()
    source_id = source["id"]

    response = client.get(f"/api/v1/tutors/{tutor_id}/knowledge-sources")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.patch(
        f"/api/v1/knowledge-sources/{source_id}",
        json={"source_name": "Updated Docs", "provider_type": "JSON"},
    )
    assert response.status_code == 200
    assert response.json()["source_name"] == "Updated Docs"
    assert response.json()["provider_type"] == ProviderType.JSON.value

    response = client.delete(f"/api/v1/knowledge-sources/{source_id}")
    assert response.status_code == 204


def test_embed_config(client):
    tutor_response = client.post(
        "/api/v1/tutors",
        json={
            "name": "Embed Tutor",
            "description": "Widget ready",
            "system_prompt": "Prompt",
            "status": "ACTIVE",
        },
    )
    tutor_id = tutor_response.json()["id"]

    response = client.get(f"/api/v1/embed/{tutor_id}/config")
    assert response.status_code == 200
    assert response.json()["name"] == "Embed Tutor"
