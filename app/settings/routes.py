from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.settings import bp
from app.extensions import db
from app.models.ai import UserAIPrefs


@bp.route("/ai", methods=["GET", "POST"])
@login_required
def ai_settings():
    prefs = current_user.ai_prefs
    if not prefs:
        prefs = UserAIPrefs(user_id=current_user.id, mode="free", free_provider="mock")
        db.session.add(prefs)
        db.session.commit()

    if request.method == "POST":
        mode = request.form.get("mode", "free")
        free_provider = request.form.get("free_provider", "mock")
        model_override = request.form.get("model_override", "").strip()

        prefs.mode = mode
        prefs.free_provider = free_provider
        prefs.model_override = model_override or None
        db.session.commit()

        flash("AI provider preferences saved successfully.", "success")
        return redirect(url_for("settings.ai_settings"))

    return render_template("settings/ai.html", prefs=prefs)
