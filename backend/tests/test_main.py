from fastapi import status

from .utils import verify_password
from backend.src.models import User

def test_create_user(client, db) -> None:
    response = client.post(
        "/auth/",
        json={
            "email": "testuser",
            "password": "testpassword",
            "full_name": "Test User",
            "experience_years": 5,
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    user = db.query(User).filter(User.email == "testuser").first()
    assert user is not None
    assert user.email == "testuser"
    assert verify_password("testpassword", user.hashed_password)
    assert user.full_name == "Test User"
    assert user.experience_years == 5
    assert user.preferred_roles == "[]"
    assert user.preferred_locations == "[]"
    assert user.preferred_sources == "[]"
    assert user.receive_email_alerts is False
    assert user.is_admin is False
    assert user.resume_url is None
    assert user.resume_text is None
    assert user.resume_parsed is None

def test_login_correct_password(client, db_with_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword",
        }
    )

    user = db_with_user.query(User).filter(User.email == "testuser").first()
    assert user is not None
    assert user.email == "testuser"
    assert verify_password("testpassword", user.hashed_password)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, db_with_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "userpassword",
        }
    )
    db_with_user.query(User).filter(User.email == "testuser").first() is not None

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
