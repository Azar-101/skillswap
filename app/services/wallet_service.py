from decimal import Decimal
from datetime import datetime, timezone
from app.extensions import db
from app.models.wallet import Wallet, WalletTransaction, CreditReservation
from app.models.booking import Booking


def calculate_credits_for_duration(duration_min: int) -> Decimal:
    """Time-based credit calculation:
    1 hour = 1.0 credit
    30 mins = 0.5 credits
    90 mins = 1.5 credits
    """
    return (Decimal(duration_min) / Decimal(60)).quantize(Decimal("0.01"))


def get_or_create_wallet(user_id: int) -> Wallet:
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        wallet = Wallet(
            user_id=user_id,
            available_balance=Decimal("0.00"),
            reserved_balance=Decimal("0.00"),
        )
        db.session.add(wallet)
        db.session.commit()
    return wallet


def add_bonus_credits(user_id: int, amount: Decimal, description: str = "Signup bonus credits") -> WalletTransaction:
    wallet = get_or_create_wallet(user_id)
    wallet.available_balance = Decimal(str(wallet.available_balance)) + Decimal(str(amount))
    
    tx = WalletTransaction(
        wallet_id=wallet.id,
        type="bonus",
        amount=amount,
        description=description,
        idempotency_key=f"bonus:{user_id}:{datetime.now(timezone.utc).timestamp()}",
    )
    db.session.add(tx)
    db.session.commit()
    return tx


def reserve_credits(booking_id: int, learner_id: int, amount: Decimal) -> CreditReservation:
    """Locks credits in escrow when teacher accepts booking."""
    wallet = get_or_create_wallet(learner_id)
    avail = Decimal(str(wallet.available_balance))
    req = Decimal(str(amount))
    
    if avail < req:
        raise ValueError(f"Insufficient credits: Available {avail}, required {req}")

    # Deduct from available and add to reserved
    wallet.available_balance = avail - req
    wallet.reserved_balance = Decimal(str(wallet.reserved_balance)) + req

    reservation = CreditReservation(
        booking_id=booking_id,
        learner_id=learner_id,
        amount=req,
        status="held",
    )
    db.session.add(reservation)

    tx = WalletTransaction(
        wallet_id=wallet.id,
        type="reserve",
        amount=-req,
        booking_id=booking_id,
        description=f"Escrow hold for Booking #{booking_id}",
        idempotency_key=f"reserve:{booking_id}",
    )
    db.session.add(tx)
    db.session.commit()
    return reservation


def release_credits(booking_id: int) -> bool:
    """Cancels credit reservation and returns credits to learner's available balance."""
    reservation = CreditReservation.query.filter_by(booking_id=booking_id, status="held").first()
    if not reservation:
        return False

    wallet = get_or_create_wallet(reservation.learner_id)
    amount = Decimal(str(reservation.amount))

    # Move from reserved back to available
    wallet.reserved_balance = max(Decimal("0.00"), Decimal(str(wallet.reserved_balance)) - amount)
    wallet.available_balance = Decimal(str(wallet.available_balance)) + amount
    reservation.status = "released"

    tx = WalletTransaction(
        wallet_id=wallet.id,
        type="release",
        amount=amount,
        booking_id=booking_id,
        description=f"Escrow released for cancelled/rejected Booking #{booking_id}",
        idempotency_key=f"release:{booking_id}",
    )
    db.session.add(tx)
    db.session.commit()
    return True


def transfer_credits_on_completion(booking: Booking) -> bool:
    """Transfers escrowed credits to teacher's wallet when session completes."""
    reservation = CreditReservation.query.filter_by(booking_id=booking.id, status="held").first()
    if not reservation:
        return False

    amount = Decimal(str(reservation.amount))
    learner_wallet = get_or_create_wallet(booking.learner_id)
    teacher_wallet = get_or_create_wallet(booking.teacher_id)

    # Learner's reserved balance is decreased
    learner_wallet.reserved_balance = max(Decimal("0.00"), Decimal(str(learner_wallet.reserved_balance)) - amount)
    
    # Teacher's available balance is increased
    teacher_wallet.available_balance = Decimal(str(teacher_wallet.available_balance)) + amount
    reservation.status = "transferred"

    # Transaction log for learner
    tx_out = WalletTransaction(
        wallet_id=learner_wallet.id,
        type="transfer_out",
        amount=-amount,
        booking_id=booking.id,
        description=f"Credits paid to {booking.teacher.full_name} for Booking #{booking.id}",
        idempotency_key=f"transfer_out:{booking.id}",
    )
    db.session.add(tx_out)

    # Transaction log for teacher
    tx_in = WalletTransaction(
        wallet_id=teacher_wallet.id,
        type="transfer_in",
        amount=amount,
        booking_id=booking.id,
        description=f"Credits earned teaching {booking.learner.full_name} ({booking.skill.name})",
        idempotency_key=f"transfer_in:{booking.id}",
    )
    db.session.add(tx_in)
    db.session.commit()
    return True


def resolve_dispute_credits(booking: Booking, decision: str) -> bool:
    """Admin resolves dispute: 'learner' (refund) or 'teacher' (award)."""
    reservation = CreditReservation.query.filter_by(booking_id=booking.id, status="held").first()
    if not reservation:
        return False

    if decision == "learner":
        return release_credits(booking.id)
    elif decision == "teacher":
        return transfer_credits_on_completion(booking)
    return False
