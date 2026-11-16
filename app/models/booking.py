from datetime import datetime, timezone, timedelta
from decimal import Decimal
import secrets
from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, index=True)
    
    start_utc = db.Column(db.DateTime, nullable=False, index=True)
    duration_min = db.Column(db.Integer, default=60, nullable=False)
    credits = db.Column(db.Numeric(8, 2), default=Decimal("1.00"), nullable=False)
    notes = db.Column(db.Text, default="")
    
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    # Statuses: 'pending', 'scheduled', 'in_progress', 'completed', 'cancelled', 'rejected', 'disputed'
    
    room_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    learner_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    teacher_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    learner = db.relationship("User", foreign_keys=[learner_id], back_populates="bookings_as_learner")
    teacher = db.relationship("User", foreign_keys=[teacher_id], back_populates="bookings_as_teacher")
    skill = db.relationship("Skill", back_populates="bookings")
    
    credit_reservation = db.relationship("CreditReservation", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    wallet_transactions = db.relationship("WalletTransaction", back_populates="booking")
    reviews = db.relationship("Review", back_populates="booking", cascade="all, delete-orphan")
    dispute = db.relationship("Dispute", back_populates="booking", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint("learner_id != teacher_id", name="check_learner_teacher_different"),
    )

    @staticmethod
    def generate_room_id() -> str:
        return f"skillswap-{secrets.token_urlsafe(16)}"

    @property
    def end_utc(self) -> datetime:
        return self.start_utc + timedelta(minutes=self.duration_min)

    @property
    def is_joinable(self) -> bool:
        # Joinable from 15 min before start until 60 min after scheduled end
        now = datetime.now(timezone.utc)
        start_buffer = self.start_utc - timedelta(minutes=15)
        end_buffer = self.end_utc + timedelta(minutes=60)
        # Note: handle timezone-naive start_utc from SQLite
        s_buf = start_buffer.replace(tzinfo=None) if self.start_utc.tzinfo is None else start_buffer
        e_buf = end_buffer.replace(tzinfo=None) if self.start_utc.tzinfo is None else end_buffer
        n_cmp = now.replace(tzinfo=None)
        return (self.status in ("scheduled", "in_progress")) and (s_buf <= n_cmp <= e_buf)

    @property
    def can_review(self) -> bool:
        return self.status == "completed"

    def __repr__(self):
        return f"<Booking id={self.id} learner={self.learner_id} teacher={self.teacher_id} status={self.status}>"
