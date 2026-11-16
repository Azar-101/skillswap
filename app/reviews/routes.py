from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.reviews import bp
from app.reviews.forms import ReviewForm
from app.extensions import db
from app.models.booking import Booking
from app.models.review import Review
from app.services.notification_service import create_notification


@bp.route("/new/<int:booking_id>", methods=["GET", "POST"])
@login_required
def new(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if current_user.id not in (booking.learner_id, booking.teacher_id):
        flash("You were not a participant in this session.", "danger")
        return redirect(url_for("bookings.index"))

    if booking.status != "completed":
        flash("Reviews can only be submitted for completed sessions.", "warning")
        return redirect(url_for("bookings.detail", booking_id=booking.id))

    # Reviewee is the other person
    reviewee = booking.teacher if current_user.id == booking.learner_id else booking.learner

    # Check if already reviewed
    existing = Review.query.filter_by(booking_id=booking.id, reviewer_id=current_user.id).first()
    if existing:
        flash("You have already reviewed this session. Thank you!", "info")
        return redirect(url_for("auth.profile", username=reviewee.username))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            booking_id=booking.id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee.id,
            rating=form.rating.data,
            comment=form.comment.data.strip(),
        )
        db.session.add(review)
        db.session.commit()

        # Notify reviewee
        create_notification(
            user_id=reviewee.id,
            type="review_received",
            title="New Review Received! ⭐",
            message=f"{current_user.full_name} gave you a {review.rating}★ review!",
            link=f"/profile/{reviewee.username}",
        )

        flash("Review submitted successfully! Thank you for supporting the community.", "success")
        return redirect(url_for("auth.profile", username=reviewee.username))

    return render_template("reviews/new.html", form=form, booking=booking, reviewee=reviewee)
