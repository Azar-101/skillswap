from datetime import datetime, timezone
from app.extensions import db


class Dispute(db.Model):
    __tablename__ = "disputes"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), unique=True, nullable=False, index=True)
    opened_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)  # 'open', 'resolved_learner', 'resolved_teacher', 'cancelled'
    resolved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resolution = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = db.relationship("Booking", back_populates="dispute")
    opened_by = db.relationship("User", foreign_keys=[opened_by_id])
    resolved_by = db.relationship("User", foreign_keys=[resolved_by_id])

    def __repr__(self):
        return f"<Dispute id={self.id} booking_id={self.booking_id} status={self.status}>"
