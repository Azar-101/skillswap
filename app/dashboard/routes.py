from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.dashboard import bp
from app.models.booking import Booking
from app.models.skills import SkillCategory, UserSkill
from app.models.ai import LearningRoadmap
from app.services.matching_service import find_matches_for_user
from app.services.wallet_service import get_or_create_wallet


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    
    # Public Landing Page
    featured_categories = SkillCategory.query.limit(6).all()
    recent_offers = UserSkill.query.filter_by(kind="offer", is_active=True).order_by(UserSkill.created_at.desc()).limit(6).all()
    return render_template("landing.html", categories=featured_categories, recent_offers=recent_offers)


@bp.route("/dashboard")
@login_required
def dashboard():
    wallet = get_or_create_wallet(current_user.id)
    
    # Upcoming sessions (learner or teacher)
    upcoming_bookings = (
        Booking.query.filter(
            (Booking.learner_id == current_user.id) | (Booking.teacher_id == current_user.id),
            Booking.status.in_(["scheduled", "in_progress"]),
        )
        .order_by(Booking.start_utc.asc())
        .limit(5)
        .all()
    )

    # Pending requests awaiting current_user's response (as teacher)
    pending_incoming = (
        Booking.query.filter_by(teacher_id=current_user.id, status="pending")
        .order_by(Booking.created_at.desc())
        .all()
    )

    # AI / Smart matches
    recommended_matches = find_matches_for_user(current_user, limit=4)

    # Recent active roadmaps
    active_roadmaps = LearningRoadmap.query.filter_by(user_id=current_user.id).order_by(LearningRoadmap.created_at.desc()).limit(3).all()

    return render_template(
        "dashboard/index.html",
        wallet=wallet,
        upcoming_bookings=upcoming_bookings,
        pending_incoming=pending_incoming,
        recommended_matches=recommended_matches,
        active_roadmaps=active_roadmaps,
    )
