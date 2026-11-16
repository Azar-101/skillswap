from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.bookings import bp
from app.bookings.forms import BookingRequestForm, DisputeForm
from app.models.booking import Booking
from app.models.skills import UserSkill
from app.services.booking_service import (
    create_booking_request,
    accept_booking,
    reject_booking,
    cancel_booking,
    confirm_booking_completion,
    open_booking_dispute,
)
from app.services.wallet_service import get_or_create_wallet, calculate_credits_for_duration


@bp.route("/")
@login_required
def index():
    tab = request.args.get("tab", "learning")
    
    learning_bookings = (
        Booking.query.filter_by(learner_id=current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    teaching_bookings = (
        Booking.query.filter_by(teacher_id=current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return render_template(
        "bookings/index.html",
        learning_bookings=learning_bookings,
        teaching_bookings=teaching_bookings,
        active_tab=tab,
    )


@bp.route("/new/<int:user_skill_id>", methods=["GET", "POST"])
@login_required
def new(user_skill_id):
    listing = UserSkill.query.get_or_404(user_skill_id)
    if listing.user_id == current_user.id:
        flash("You cannot book a session with yourself.", "warning")
        return redirect(url_for("skills.index"))

    teacher = listing.user
    form = BookingRequestForm()
    
    # Pre-select duration from listing
    if request.method == "GET":
        form.duration_min.data = listing.session_minutes

    wallet = get_or_create_wallet(current_user.id)
    credit_cost = calculate_credits_for_duration(form.duration_min.data or 60)

    if form.validate_on_submit():
        start_dt = form.start_time.data
        duration = form.duration_min.data
        notes = form.notes.data or ""
        try:
            booking = create_booking_request(
                learner_id=current_user.id,
                teacher_id=teacher.id,
                skill_id=listing.skill_id,
                start_utc=start_dt,
                duration_min=duration,
                notes=notes,
            )
            flash(f"Swap request sent to {teacher.full_name}! They will review your time proposal.", "success")
            return redirect(url_for("bookings.detail", booking_id=booking.id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "bookings/new.html",
        form=form,
        listing=listing,
        teacher=teacher,
        wallet=wallet,
        credit_cost=credit_cost,
    )


@bp.route("/<int:booking_id>", methods=["GET", "POST"])
@login_required
def detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if current_user.id not in (booking.learner_id, booking.teacher_id) and not current_user.is_admin:
        flash("You do not have access to this booking.", "danger")
        return redirect(url_for("bookings.index"))

    dispute_form = DisputeForm()

    return render_template(
        "bookings/detail.html",
        booking=booking,
        dispute_form=dispute_form,
    )


@bp.route("/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept(booking_id):
    try:
        accept_booking(booking_id, current_user.id)
        flash("You accepted the swap request! Credits are now secured in escrow.", "success")
    except Exception as e:
        flash(f"Error accepting booking: {e}", "danger")
    return redirect(url_for("bookings.detail", booking_id=booking_id))


@bp.route("/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject(booking_id):
    try:
        reject_booking(booking_id, current_user.id)
        flash("You declined the swap request.", "info")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("bookings.detail", booking_id=booking_id))


@bp.route("/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel(booking_id):
    try:
        cancel_booking(booking_id, current_user.id)
        flash("Booking has been cancelled. Any reserved credits were returned.", "info")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("bookings.detail", booking_id=booking_id))


@bp.route("/<int:booking_id>/confirm", methods=["POST"])
@login_required
def confirm(booking_id):
    try:
        confirm_booking_completion(booking_id, current_user.id)
        flash("Session confirmed as completed! Escrow credits were transferred to the teacher.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("bookings.detail", booking_id=booking_id))


@bp.route("/<int:booking_id>/dispute", methods=["POST"])
@login_required
def dispute(booking_id):
    form = DisputeForm()
    if form.validate_on_submit():
        try:
            open_booking_dispute(booking_id, current_user.id, form.reason.data)
            flash("Dispute raised. Platform admin has been notified and will review the session.", "warning")
        except Exception as e:
            flash(f"Error opening dispute: {e}", "danger")
    else:
        flash("Please provide a valid dispute reason (min 10 characters).", "danger")

    return redirect(url_for("bookings.detail", booking_id=booking_id))
