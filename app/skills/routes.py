from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.skills import bp
from app.skills.forms import UserSkillForm
from app.extensions import db
from app.models.skills import SkillCategory, Skill, UserSkill


@bp.route("/")
def index():
    query_str = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    kind = request.args.get("kind", "offer")  # default to teaching offers
    level = request.args.get("level", "")

    skills_query = UserSkill.query.filter_by(is_active=True)

    if kind:
        skills_query = skills_query.filter_by(kind=kind)

    if level:
        skills_query = skills_query.filter_by(level=level)

    if category_id:
        skills_query = skills_query.join(Skill).filter(Skill.category_id == category_id)

    if query_str:
        search_filter = f"%{query_str}%"
        skills_query = skills_query.join(Skill).filter(
            (Skill.name.ilike(search_filter))
            | (UserSkill.description.ilike(search_filter))
        )

    listings = skills_query.order_by(UserSkill.created_at.desc()).all()
    categories = SkillCategory.query.order_by(SkillCategory.name).all()

    return render_template(
        "skills/index.html",
        listings=listings,
        categories=categories,
        selected_category=category_id,
        selected_kind=kind,
        selected_level=level,
        search_query=query_str,
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = UserSkillForm()
    categories = SkillCategory.query.order_by(SkillCategory.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        clean_name = form.skill_name.data.strip()
        # Find or create skill in this category
        skill = Skill.query.filter_by(category_id=form.category_id.data, name=clean_name).first()
        if not skill:
            skill = Skill(category_id=form.category_id.data, name=clean_name)
            db.session.add(skill)
            db.session.flush()

        # Check if user already listed this exact skill & kind
        existing = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill.id, kind=form.kind.data).first()
        if existing:
            existing.level = form.level.data
            existing.description = form.description.data.strip()
            existing.session_minutes = form.session_minutes.data
            existing.is_active = True
            db.session.commit()
            flash("Updated your existing listing for this skill.", "info")
            return redirect(url_for("auth.profile", username=current_user.username))

        user_skill = UserSkill(
            user_id=current_user.id,
            skill_id=skill.id,
            kind=form.kind.data,
            level=form.level.data,
            session_minutes=form.session_minutes.data,
            description=form.description.data.strip(),
            is_active=True,
        )
        db.session.add(user_skill)
        db.session.commit()

        action_text = "offering to teach" if form.kind.data == "offer" else "requesting to learn"
        flash(f"Successfully added your listing: {action_text} '{clean_name}'!", "success")
        return redirect(url_for("auth.profile", username=current_user.username))

    return render_template("skills/new.html", form=form)


@bp.route("/<int:skill_id>")
def detail(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    teachers = UserSkill.query.filter_by(skill_id=skill.id, kind="offer", is_active=True).all()
    learners = UserSkill.query.filter_by(skill_id=skill.id, kind="want", is_active=True).all()
    return render_template("skills/detail.html", skill=skill, teachers=teachers, learners=learners)


@bp.route("/delete/<int:user_skill_id>", methods=["POST"])
@login_required
def delete(user_skill_id):
    listing = UserSkill.query.get_or_404(user_skill_id)
    if listing.user_id != current_user.id and not current_user.is_admin:
        flash("You do not have permission to delete this listing.", "danger")
        return redirect(url_for("skills.index"))

    db.session.delete(listing)
    db.session.commit()
    flash("Skill listing removed.", "info")
    return redirect(url_for("auth.profile", username=current_user.username))
