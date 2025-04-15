from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

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
