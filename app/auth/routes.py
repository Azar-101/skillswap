from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, ProfileEditForm
from app.extensions import db
from app.models.user import User
from app.services.wallet_service import add_bonus_credits, get_or_create_wallet
from app.services.notification_service import create_notification


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            headline=form.headline.data.strip() if form.headline.data else "",
            role="user",
            status="active",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Initialize wallet and grant signup bonus credits
        get_or_create_wallet(user.id)
        bonus = current_app.config.get("SIGNUP_BONUS_CREDITS")
        if bonus and bonus > 0:
            add_bonus_credits(user.id, bonus, description="Welcome gift: 2.0 Free Learning Credits")

        # Send welcome notification
        create_notification(
            user_id=user.id,
            type="welcome",
            title="Welcome to SkillSwap! 🎉",
            message=f"You received {bonus} free credits! Browse our skill directory to book your first exchange session.",
            link="/skills",
        )

        login_user(user)
        flash(f"Welcome to SkillSwap, {user.full_name}! We credited {bonus} free credits to your wallet.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email.data.strip().lower()
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        if user and user.check_password(form.password.data):
            if user.status != "active":
                flash("Your account has been suspended. Please contact admin support.", "danger")
                return redirect(url_for("auth.login"))

            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard.index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("auth/profile.html", user=user)


@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileEditForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.headline = form.headline.data.strip()
        current_user.location = form.location.data.strip()
        current_user.timezone = form.timezone.data.strip()
        current_user.bio = form.bio.data.strip()
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("auth.profile", username=current_user.username))

    return render_template("auth/edit_profile.html", form=form)
