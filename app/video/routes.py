from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.video import bp
from app.models.booking import Booking
from app.extensions import db


@bp.route("/<room_id>")
@login_required
def room(room_id):
    booking = Booking.query.filter_by(room_id=room_id).first_or_404()

    if current_user.id not in (booking.learner_id, booking.teacher_id) and not current_user.is_admin:
        flash("You are not authorized to enter this video room.", "danger")
        return redirect(url_for("bookings.index"))

    # Update status to in_progress if currently scheduled
    if booking.status == "scheduled":
        booking.status = "in_progress"
        db.session.commit()

    jitsi_domain = current_app.config.get("JITSI_DOMAIN", "meet.jit.si")
    jitsi_script = current_app.config.get("JITSI_SCRIPT_URL", "https://meet.jit.si/external_api.js")

    return render_template(
        "video/room.html",
        booking=booking,
        jitsi_domain=jitsi_domain,
        jitsi_script=jitsi_script,
        room_name=booking.room_id,
    )
