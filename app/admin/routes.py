from functools import wraps
from datetime import datetime, timezone
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.admin import bp
from app.extensions import db
from app.models.user import User
from app.models.skills import Skill, SkillCategory, UserSkill
from app.models.booking import Booking
from app.models.dispute import Dispute
from app.models.wallet import Wallet
from app.models.ai import AIUsageLog
from app.services.wallet_service import resolve_dispute_credits
from app.services.notification_service import create_notification


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Administrator privileges are required to access this area.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@bp.route("/")
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(status="active").count()
    total_skills = UserSkill.query.count()
    total_bookings = Booking.query.count()
    completed_bookings = Booking.query.filter_by(status="completed").count()
    open_disputes = Dispute.query.filter_by(status="open").count()
    
    # Calculate total credits
    wallets = Wallet.query.all()
    total_credits = sum((Decimal(str(w.available_balance or 0)) + Decimal(str(w.reserved_balance or 0))) for w in wallets)

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    recent_ai_logs = AIUsageLog.query.order_by(AIUsageLog.created_at.desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        active_users=active_users,
        total_skills=total_skills,
        total_bookings=total_bookings,
        completed_bookings=completed_bookings,
        open_disputes=open_disputes,
        total_credits=total_credits,
        recent_users=recent_users,
        recent_bookings=recent_bookings,
        recent_ai_logs=recent_ai_logs,
    )


@bp.route("/users")
@admin_required
def users():
    search = request.args.get("q", "").strip()
    query = User.query
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.full_name.ilike(f"%{search}%"))
        )
    user_list = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=user_list, search=search)


@bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot alter your own admin status.", "warning")
        return redirect(url_for("admin.users"))

    user.status = "suspended" if user.status == "active" else "active"
    db.session.commit()
    flash(f"User {user.username} is now {user.status}.", "info")
    return redirect(url_for("admin.users"))


@bp.route("/bookings")
@admin_required
def bookings():
    status_filter = request.args.get("status")
    query = Booking.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=all_bookings, current_status=status_filter)


@bp.route("/disputes")
@admin_required
def disputes():
    all_disputes = Dispute.query.order_by(Dispute.created_at.desc()).all()
    return render_template("admin/disputes.html", disputes=all_disputes)


@bp.route("/disputes/<int:dispute_id>/resolve", methods=["POST"])
@admin_required
def resolve_dispute(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    decision = request.form.get("decision")  # 'learner' or 'teacher'
    notes = request.form.get("resolution_notes", "").strip()

    if decision not in ("learner", "teacher"):
        flash("Invalid dispute resolution target.", "danger")
        return redirect(url_for("admin.disputes"))

    booking = dispute.booking
    resolve_dispute_credits(booking, decision)

    dispute.status = f"resolved_{decision}"
    dispute.resolved_by_id = current_user.id
    dispute.resolution = notes
    dispute.resolved_at = datetime.now(timezone.utc)
    booking.status = "completed" if decision == "teacher" else "cancelled"
    db.session.commit()

    # Send notifications
    winner_id = booking.learner_id if decision == "learner" else booking.teacher_id
    create_notification(
        user_id=winner_id,
        type="dispute_resolved",
        title="Dispute Resolved in Your Favor",
        message=f"Admin resolved dispute #{dispute.id}: {notes}",
        link=f"/bookings/{booking.id}",
    )

    flash(f"Dispute resolved in favor of {decision}. Credits handled accordingly.", "success")
    return redirect(url_for("admin.disputes"))


@bp.route("/seed-data", methods=["POST"])
@admin_required
def seed_data():
    from app.services.seed_service import seed_database
    seed_database()
    flash("Database successfully seeded with realistic demo users, skills, bookings, and reviews!", "success")
    return redirect(url_for("admin.dashboard"))
