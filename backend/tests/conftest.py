import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from ..src.deps import get_db
from ..src.main import app
from ..src.models import Base, User
from ..src.utils import hash_password, verify_password


@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    yield db
    db.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_with_user(db):
    user = User(
        email="testuser@gmail.com",
        hashed_password=hash_password("Testpassword123"),
        full_name="Test User",
        experience_years=5,
        preferred_roles="[]",
        preferred_locations="[]",
        preferred_sources="[]",
        receive_email_alerts=False,
        is_admin=False,
        resume_url=None,
    )
    db.add(user)
    db.commit()
    yield db
    db.delete(user)
    db.commit()


@pytest.fixture(scope="function")
def token(client, db_with_user):
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
    data = response.json()
    assert "access_token" in data
    yield data["access_token"]
