from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey, Text, Date, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import date

db = SQLAlchemy()


class Users(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    firstname: Mapped[str] = mapped_column(String(120), nullable=False)
    lastname: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    def generate_hash(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'category': self.category
        }


class Meteorological(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    freak: Mapped[str] = mapped_column(String(120), nullable=False)
    cat: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    recommendation_list: Mapped[list["Recommendation"]] = relationship(
        back_populates="freak", cascade="all, delete-orphan")
    work_recommendation_list: Mapped[list["WorkRecommendation"]] = relationship(
        back_populates="freak", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "freak": self.freak,
            "cat": self.cat,
            "title": self.title,
            "recommendation": [tip.serialize() for tip in self.recommendation_list],
            "work_recommendation": [tip.serialize() for tip in self.work_recommendation_list]
        }


class Recommendation(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    freak_id: Mapped[int] = mapped_column(ForeignKey("meteorological.id"))
    freak: Mapped["Meteorological"] = relationship(
        back_populates="recommendation_list")
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "freak_id": self.freak_id,
            "recommendation": self.recommendation
        }


class WorkRecommendation(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    freak_id: Mapped[int] = mapped_column(ForeignKey("meteorological.id"))
    freak: Mapped["Meteorological"] = relationship(
        back_populates="work_recommendation_list")
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    work_recommendation: Mapped[str] = mapped_column(
        Text, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "freak_id": self.freak_id,
            "type": self.type,
            "work_recommendation": self.work_recommendation
        }


class Alerts(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    zone: Mapped[str] = mapped_column(String(120), nullable=False)
    parameter: Mapped[str] = mapped_column(String(120), nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start: Mapped[str] = mapped_column(String(8), nullable=False)
    end: Mapped[str] = mapped_column(String(8), nullable=False)
    date: Mapped[date] = mapped_column(Date, server_default=func.now())
    origin: Mapped[str] = mapped_column(
        String(20), nullable=False, default='aemet')
    event: Mapped[str] = mapped_column(
        String(30), nullable=False, default='nueva')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    def serialize(self):
        return {
            "id": self.id,
            "zone": self.zone,
            "parameter": self.parameter,
            "level": self.level,
            "description": self.description,
            "start": self.start,
            "end": self.end,
            "date": self.date.isoformat() if self.date else None,
            "origin": self.origin,
            "event": self.event,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
