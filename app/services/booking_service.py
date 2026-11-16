from datetime import datetime, timezone
from app.extensions import db
from app.models.booking import Booking
from app.models.skills import Skill
from app.models.dispute import Dispute
from app.services.wallet_service import (
    calculate_credits_for_duration,
    reserve_credits,
    release_credits,
    transfer_credits_on_completion,
    get_or_create_wallet,
)
from app.services.notification_service import create_notification


def create_booking_request(
    learner_id: int, teacher_id: int, skill_id: int, start_utc: datetime, duration_min: int, notes: str = ""
) -> Booking:
    if learner_id == teacher_id:
        raise ValueError("You cannot book a session with yourself.")

    skill = db.session.get(Skill, skill_id)
    if not skill:
        raise ValueError("Selected skill was not found.")

    credit_cost = calculate_credits_for_duration(duration_min)
    learner_wallet = get_or_create_wallet(learner_id)

    if learner_wallet.available_balance < credit_cost:
        raise ValueError(
            f"You need {credit_cost} credits for this {duration_min}-minute session. "
            f"Your current balance is {learner_wallet.available_balance} credits. "
            f"Teach a skill to earn more credits!"
        )

    room_id = Booking.generate_room_id()

    booking = Booking(
        learner_id=learner_id,
        teacher_id=teacher_id,
        skill_id=skill_id,
        start_utc=start_utc,
        duration_min=duration_min,
        credits=credit_cost,
        notes=notes,
        status="pending",
        room_id=room_id,
    )
    db.session.add(booking)
    db.session.commit()

    # Notify teacher
    create_notification(
        user_id=teacher_id,
        type="booking_request",
        title="New Swap Request!",
        message=f"{booking.learner.full_name} wants to learn {skill.name} ({duration_min} mins).",
        link=f"/bookings/{booking.id}",
    )

    return booking


def accept_booking(booking_id: int, teacher_id: int) -> Booking:
    booking = Booking.query.get_or_404(booking_id)
    if booking.teacher_id != teacher_id:
        raise PermissionError("Only the assigned teacher can accept this booking.")

    if booking.status != "pending":
        raise ValueError(f"Booking cannot be accepted from state '{booking.status}'.")

    # Reserve credits from learner in escrow
    reserve_credits(booking.id, booking.learner_id, booking.credits)
    
    booking.status = "scheduled"
    booking.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    # Notify learner
    create_notification(
        user_id=booking.learner_id,
        type="booking_accepted",
        title="Session Confirmed! 🎉",
        message=f"{booking.teacher.full_name} accepted your {booking.skill.name} session.",
        link=f"/bookings/{booking.id}",
    )

    return booking


def reject_booking(booking_id: int, teacher_id: int, reason: str = "") -> Booking:
    booking = Booking.query.get_or_404(booking_id)
    if booking.teacher_id != teacher_id:
        raise PermissionError("Only the assigned teacher can reject this booking.")

    if booking.status not in ("pending",):
        raise ValueError(f"Booking cannot be rejected from state '{booking.status}'.")

    booking.status = "rejected"
    booking.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    create_notification(
        user_id=booking.learner_id,
        type="booking_rejected",
        title="Session Declined",
        message=f"{booking.teacher.full_name} was unable to accept your session request. No credits were deducted.",
        link=f"/bookings/{booking.id}",
    )

    return booking


def cancel_booking(booking_id: int, user_id: int) -> Booking:
    booking = Booking.query.get_or_404(booking_id)
    if user_id not in (booking.learner_id, booking.teacher_id):
        raise PermissionError("You are not a participant in this booking.")

    if booking.status in ("completed", "cancelled", "disputed"):
        raise ValueError(f"Cannot cancel a booking with status '{booking.status}'.")

    # Release held escrow if scheduled
    if booking.status == "scheduled":
        release_credits(booking.id)

    booking.status = "cancelled"
    booking.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    other_user_id = booking.teacher_id if user_id == booking.learner_id else booking.learner_id
    create_notification(
        user_id=other_user_id,
        type="booking_cancelled",
        title="Session Cancelled",
        message=f"Session for {booking.skill.name} was cancelled.",
        link=f"/bookings/{booking.id}",
    )

    return booking


def confirm_booking_completion(booking_id: int, user_id: int) -> Booking:
    """Either party can confirm session completion; releases escrow to teacher."""
    booking = Booking.query.get_or_404(booking_id)
    if user_id not in (booking.learner_id, booking.teacher_id):
        raise PermissionError("You are not a participant in this booking.")

    if booking.status not in ("scheduled", "in_progress"):
        if booking.status == "completed":
            return booking
        raise ValueError(f"Cannot complete booking with status '{booking.status}'.")

    if user_id == booking.learner_id:
        booking.learner_confirmed = True
    if user_id == booking.teacher_id:
        booking.teacher_confirmed = True

    # Complete if confirmed or if either participant confirms
    booking.status = "completed"
    booking.updated_at = datetime.now(timezone.utc)
    
    # Transfer escrow to teacher
    transfer_credits_on_completion(booking)

    # Notify both
    create_notification(
        user_id=booking.teacher_id,
        type="credits_received",
        title="Credits Earned! ⚡",
        message=f"You earned +{booking.credits} credits teaching {booking.learner.full_name}!",
        link="/wallet",
    )
    create_notification(
        user_id=booking.learner_id,
        type="session_completed",
        title="Session Completed",
        message=f"Please leave a review for {booking.teacher.full_name}!",
        link=f"/reviews/new/{booking.id}",
    )

    db.session.commit()
    return booking


def open_booking_dispute(booking_id: int, user_id: int, reason: str) -> Dispute:
    booking = Booking.query.get_or_404(booking_id)
    if user_id not in (booking.learner_id, booking.teacher_id):
        raise PermissionError("You are not a participant in this booking.")

    if booking.dispute:
        return booking.dispute

    booking.status = "disputed"
    booking.updated_at = datetime.now(timezone.utc)

    dispute = Dispute(
        booking_id=booking.id,
        opened_by_id=user_id,
        reason=reason,
        status="open",
    )
    db.session.add(dispute)
    db.session.commit()

    create_notification(
        user_id=booking.learner_id if user_id == booking.teacher_id else booking.teacher_id,
        type="dispute_opened",
        title="Dispute Opened",
        message=f"A dispute was opened for session #{booking.id}. Admin will review.",
        link=f"/bookings/{booking.id}",
    )

    return dispute
