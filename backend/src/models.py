from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)

    experience_years = Column(Integer)
    preferred_roles = Column(String)  # JSON or String representation of array
    preferred_locations = Column(String)  # JSON or String representation of array
    preferred_sources = Column(String)  # JSON or String representation of array

    receive_email_alerts = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    resume_url = Column(String)  # Path or S3 URL to uploaded resume
    resume_text = Column(String)  # Parsed plain text of the resume
    resume_parsed = Column(String)  # Structured JSON (skills, education, etc.)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, index=True)
    description = Column(Text)
    url = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)
    role = Column(String, nullable=False)

    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String, default="USD")
    salary_from_levels_fyi = Column(Boolean, default=False)

    posted_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
