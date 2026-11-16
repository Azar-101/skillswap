from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    available_balance = db.Column(db.Numeric(8, 2), default=Decimal("0.00"), nullable=False)
    reserved_balance = db.Column(db.Numeric(8, 2), default=Decimal("0.00"), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="wallet")
    transactions = db.relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan", order_by="desc(WalletTransaction.created_at)"
    )

    @property
    def total_balance(self) -> Decimal:
        return Decimal(str(self.available_balance or 0)) + Decimal(str(self.reserved_balance or 0))

    def __repr__(self):
        return f"<Wallet user_id={self.user_id} avail={self.available_balance} reserved={self.reserved_balance}>"


class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)  # 'bonus', 'reserve', 'release', 'transfer_in', 'transfer_out'
    amount = db.Column(db.Numeric(8, 2), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    description = db.Column(db.String(255), default="")
    idempotency_key = db.Column(db.String(100), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    wallet = db.relationship("Wallet", back_populates="transactions")
    booking = db.relationship("Booking", back_populates="wallet_transactions")

    def __repr__(self):
        return f"<WalletTransaction id={self.id} type={self.type} amount={self.amount}>"


class CreditReservation(db.Model):
    __tablename__ = "credit_reservations"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), unique=True, nullable=False, index=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.String(20), default="held", nullable=False)  # 'held', 'released', 'transferred'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = db.relationship("Booking", back_populates="credit_reservation")
    learner = db.relationship("User", foreign_keys=[learner_id])

    def __repr__(self):
        return f"<CreditReservation booking_id={self.booking_id} amount={self.amount} status={self.status}>"
