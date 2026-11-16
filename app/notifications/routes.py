from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.notifications import bp
from app.models.notification import Notification
from app.services.notification_service import mark_notification_read, mark_all_notifications_read


@bp.route("/")
@login_required
def index():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("notifications/index.html", notifications=notifications)


@bp.route("/read/<int:id>", methods=["POST"])
@login_required
def mark_read(id):
    mark_notification_read(id, current_user.id)
    next_page = request.referrer or url_for("notifications.index")
    return redirect(next_page)


@bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():
    mark_all_notifications_read(current_user.id)
    flash("All notifications marked as read.", "info")
    return redirect(url_for("notifications.index"))
