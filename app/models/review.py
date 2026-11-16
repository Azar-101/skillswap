from datetime import datetime, timezone
from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    reviewee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = db.relationship("Booking", back_populates="reviews")
    reviewer = db.relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = db.relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")

    __table_args__ = (
        db.UniqueConstraint("booking_id", "reviewer_id", name="uq_booking_reviewer"),
    )

    def __repr__(self):
        return f"<Review id={self.id} rating={self.rating} from={self.reviewer_id} to={self.reviewee_id}>"
