from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # 'user', 'admin'
    status = db.Column(db.String(20), default="active", nullable=False)  # 'active', 'suspended'
    bio = db.Column(db.Text, default="")
    headline = db.Column(db.String(150), default="")
    location = db.Column(db.String(100), default="")
    timezone = db.Column(db.String(50), default="UTC")
    avatar_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    wallet = db.relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = db.relationship("UserSkill", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    availability = db.relationship("AvailabilitySlot", back_populates="user", cascade="all, delete-orphan")
    
    bookings_as_learner = db.relationship(
        "Booking", foreign_keys="Booking.learner_id", back_populates="learner", lazy="dynamic"
    )
    bookings_as_teacher = db.relationship(
        "Booking", foreign_keys="Booking.teacher_id", back_populates="teacher", lazy="dynamic"
    )
    
    reviews_given = db.relationship(
        "Review", foreign_keys="Review.reviewer_id", back_populates="reviewer", lazy="dynamic"
    )
    reviews_received = db.relationship(
        "Review", foreign_keys="Review.reviewee_id", back_populates="reviewee", lazy="dynamic"
    )
    
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    roadmaps = db.relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    quizzes = db.relationship("GeneratedQuiz", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    ai_conversations = db.relationship("AIConversation", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    ai_prefs = db.relationship("UserAIPrefs", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def average_rating(self) -> float:
        reviews = self.reviews_received.all()
        if not reviews:
            return 5.0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def review_count(self) -> int:
        return self.reviews_received.count()

    @property
    def completed_sessions_count(self) -> int:
        from app.models.booking import Booking
        teacher_completed = self.bookings_as_teacher.filter_by(status="completed").count()
        learner_completed = self.bookings_as_learner.filter_by(status="completed").count()
        return teacher_completed + learner_completed

    @property
    def skills_offered(self):
        return self.skills.filter_by(kind="offer", is_active=True).all()

    @property
    def skills_wanted(self):
        return self.skills.filter_by(kind="want", is_active=True).all()

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
