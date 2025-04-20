from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from io import BytesIO
import json
import os
from fastapi import status

from ..src.main import expire_jobs, mark_jobs_inactive
from ..src.models import Job, User
from ..src.utils import verify_password


def test_create_user(client, db) -> None:
    # Prepare the stringified JSON for the `user` field
    user_data = {
        "email": "testuser@gmail.com",
        "password": "Testpassword123",
        "repeat_password": "Testpassword123",
        "full_name": "Test User",
        "experience_years": 5,
    }
    user_json = json.dumps(user_data)

    # Simulate a PDF file for the `resume` field
    resume_content = b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000067 00000 n \n0000000124 00000 n \ntrailer << /Size 4 /Root 1 0 R >>\nstartxref\n179\n%%EOF"
    resume_file = BytesIO(resume_content)
    resume_file.name = "resume.pdf"

    # Send the request as `multipart/form-data`
    response = client.post(
        "/auth/",
        data={"user": user_json},  # Send the `user` field as stringified JSON
        files={
            "resume": ("resume.pdf", resume_file, "application/pdf")
        },  # Attach the resume file
    )

    user: User = db.query(User).filter(User.email == "testuser@gmail.com").first()
    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    user_dict = json.loads(response.content)
    assert user is not None
    assert user.email == "testuser@gmail.com"
    assert user_dict["email"] == "testuser@gmail.com"
    assert verify_password("Testpassword123", user.hashed_password)
    assert not "hashed_password" in user_dict and not "password" in user_dict
    assert user.full_name == "Test User"
    assert user_dict["full_name"] == "Test User"
    assert user.experience_years == 5
    assert user_dict["experience_years"] == 5
    assert user.preferred_roles == "[]"
    assert user_dict["preferred_roles"] == "[]"
    assert user.preferred_locations == "[]"
    assert user_dict["preferred_locations"] == "[]"
    assert user.preferred_sources == "[]"
    assert user_dict["preferred_sources"] == "[]"
    assert user.receive_email_alerts is False
    assert user_dict["receive_email_alerts"] is False
    assert user.is_admin is False
    assert user_dict["is_admin"] is False
    assert user.resume_url == os.path.join("static", user.email, resume_file.name)
    assert user_dict["resume_url"] == os.path.join(
        "static", user.email, resume_file.name
    )


def test_login_correct_password(client, db_with_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser@gmail.com",
            "password": "Testpassword123",
        },
    )

    user = db_with_user.query(User).filter(User.email == "testuser@gmail.com").first()
    assert user is not None
    assert user.email == "testuser@gmail.com"
    assert verify_password("Testpassword123", user.hashed_password)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db_with_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser@gmail.com",
            "password": "Testpassword1234",
        },
    )
    assert (
        db_with_user.query(User).filter(User.email == "testuser@gmail.com").first()
        is not None
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_expire_jobs(db):
    db.bulk_save_objects(
        [
            Job(
                title="Random Title",
                company="Random Company",
                url="Random URL 1",
                source="Random Source",
                role="Random Role",
                posted_at=datetime.now(timezone.utc),
            ),
            Job(
                title="Random Title",
                company="Random Company",
                url="Random URL 2",
                source="Random Source",
                role="Random Role",
                posted_at=datetime.now(timezone.utc) - relativedelta(hours=24 * 7 + 12),
            ),
            Job(
                title="Random Title",
                company="Random Company",
                url="Random URL 3",
                source="Random Source",
                role="Random Role",
                posted_at=datetime.now(timezone.utc) - relativedelta(days=9),
            ),
        ]
    )
    db.commit()
    expire_jobs(db)
    assert len(db.query(Job).all()) == 3
    assert len(db.query(Job).filter(Job.is_active == True).all()) == 3
    mark_jobs_inactive(db)
    assert len(db.query(Job).all()) == 3
    assert len(db.query(Job).filter(Job.is_active == True).all()) == 1
    expire_jobs(db)
    assert len(db.query(Job).all()) == 1
