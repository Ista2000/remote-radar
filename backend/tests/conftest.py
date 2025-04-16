import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from ..src.deps import get_db
from ..src.main import app
from ..src.models import Base, User
from ..src.utils import hash_password


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
        email="testuser",
        hashed_password=hash_password("testpassword"),
        full_name="Test User",
        experience_years=5,
        preferred_roles="[]",
        preferred_locations="[]",
        preferred_sources="[]",
        receive_email_alerts=False,
        is_admin=False,
        resume_url=None,
        resume_text=None,
        resume_parsed=None,
    )
    db.add(user)
    db.commit()
    yield db
    db.delete(user)
    db.commit()
