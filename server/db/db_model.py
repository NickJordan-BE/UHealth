from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
    DateTime,
    Boolean,
    UUID,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from utils.token import JWT_REFRESH_EXP
from dataclasses import dataclass
import os

load_dotenv()

USER = os.getenv("PG_USER")
PASSWORD = os.getenv("PG_PASS")
HOST = os.getenv("PG_HOST")
PORT = os.getenv("PG_PORT")
DBNAME = os.getenv("PG_DATABASE")

DATABASE_URL = (
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
)

engine = create_engine(DATABASE_URL, poolclass=NullPool)
Base = declarative_base()

@dataclass
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username:str = Column(Text, nullable=False, unique=True)
    email:str = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    is_active:bool = Column(Boolean, nullable=False, default=True)
    created_at:timezone = Column(
        DateTime(timezone=True), nullable=True, default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    last_login = Column(DateTime(timezone=True), nullable=True)
    role:str = Column(
        ENUM("doctor", "patient", "admin", name="role"),
        nullable=False,
        default="patient",
    )

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)

    __table_args__ = (
        CheckConstraint("length(username) <= 20", name="users_username_check"),
        CheckConstraint(
            "role IN ('doctor', 'patient', 'admin')", name="users_role_check"
        ),
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_active", "is_active"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"


@dataclass
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    refresh_token_hash:str = Column(Text, nullable=False, unique=True)
    refresh_expires_at:datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(seconds=JWT_REFRESH_EXP),
    )
    refresh_created_at:datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    refresh_is_revoked = Column(Boolean, nullable=False, default=False)

    user = relationship("Users", back_populates="tokens")

    __table_args__ = (
        Index("idx_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_hash", "refresh_token_hash"),
        Index("idx_refresh_expires_at", "refresh_expires_at"),
        Index("idx_tokens_active", "refresh_is_revoked", "refresh_expires_at"),
    )

    def __repr__(self):
        return f"<Token(id={self.id}, user_id={self.user_id}, expires_at='{self.refresh_expires_at}', revoked={self.refresh_is_revoked})>"

    def is_valid(self):
        """Check if token is still valid (not expired and not revoked)"""
        cur_time = datetime.now(timezone.utc)
        return self.refresh_expires_at > cur_time

    def revoke(self):
        """Revoke the token"""
        self.refresh_is_revoked = True


@dataclass
class Doctor(Base):
    __tablename__ = "doctor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id:UUID = Column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        server_default=func.gen_random_uuid(),
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    first_name:str = Column(Text, nullable=False)
    last_name:str = Column(Text, nullable=True)

    user = relationship("Users", back_populates="doctor")
    patients = relationship("Patient", back_populates="doctor")
    diagnoses = relationship("Diagnosis", back_populates="doctor")

    __table_args__ = (
        Index("idx_doctor_user_id", "user_id"),
        Index("idx_doctor_names", "last_name", "first_name"),
    )

    def __repr__(self):
        return f"<Doctor(id={self.id}, user_id={self.user_id}, first_name={self.first_name}, last_name={self.last_name})>"


@dataclass
class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    first_name:str = Column(Text, nullable=False)
    last_name:str = Column(Text, nullable=False)
    doctor_id = Column(
        Integer,
        ForeignKey("doctor.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    user = relationship("Users", back_populates="patient")
    doctor = relationship("Doctor", back_populates="patients")
    images = relationship("Image", back_populates="patient")
    diagnoses = relationship("Diagnosis", back_populates="patient")

    __table_args__ = (
        Index("idx_patient_user_id", "user_id"),
        Index("idx_patient_names", "last_name", "first_name"),
        Index("idx_patient_doctor_id", "doctor_id"),
    )

    def __repr__(self):
        return f"<Patient(id={self.id}, user_id={self.user_id}, first_name={self.first_name}, last_name={self.last_name})>"


@dataclass
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    orig_path:str = Column(Text, nullable=False, unique=True)
    orig_image_name:str = Column(Text, nullable=False, unique=True)
    mod_path:str = Column(Text, nullable=False, unique=True)
    mod_image_name:str = Column(Text, nullable=False, unique=True)

    patient = relationship("Patient", back_populates="images")
    diagnoses = relationship(
        "Diagnosis", back_populates="image", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_images_patient_id", "patient_id"),
        Index("idx_mod_images_name", "mod_image_name"),
        Index("idx_orig_images_name", "orig_image_name"),
    )

    def __repr__(self):
        return f"<Image(id={self.id}, name='{self.image_name}', path='{self.path}')>"


@dataclass
class Diagnosis(Base):
    __tablename__ = "diagnosis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(
        Integer,
        ForeignKey("images.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    original_image_path:str = Column(Text, nullable=False)
    modified_image_path:str = Column(Text, nullable=False)
    diagnosis_name:str = Column(Text, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    doctor_id = Column(
        Integer,
        ForeignKey("doctor.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    image = relationship("Image", back_populates="diagnoses")
    patient = relationship("Patient", back_populates="diagnoses")
    doctor = relationship("Doctor", back_populates="diagnoses")

    __table_args__ = (
        Index("idx_diagnosis_image_id", "image_id"),
        Index("idx_diagnosis_patient_id", "patient_id"),
        Index("idx_diagnosis_doctor_id", "doctor_id"),
        Index("idx_diagnosis_name", "diagnosis_name"),
        Index("idx_diagnosis_paths", "original_image_path", "modified_image_path"),
    )

    def __repr__(self):
        return f"<Diagnosis(id={self.id}, name='{self.diagnosis_name}')>"


cur_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    with engine.connect() as connection:
        print("Connected to supabase!")
except Exception as e:
    print(f"Failed to connect to supabase: {e}")

