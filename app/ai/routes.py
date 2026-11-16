import json
from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.ai import bp
from app.ai.forms import RoadmapRequestForm, QuizRequestForm
from app.extensions import db
from app.models.ai import (
    LearningRoadmap,
    RoadmapProgress,
    GeneratedQuiz,
    QuizAttempt,
    AIConversation,
    AIMessage,
)
from app.services.ai_service import AIService
from app.services.matching_service import find_matches_for_user


@bp.route("/matching")
@login_required
def matching():
    matches = find_matches_for_user(current_user, limit=20)
    return render_template("ai/matching.html", matches=matches)


@bp.route("/roadmap", methods=["GET", "POST"])
@login_required
def roadmap_index():
    form = RoadmapRequestForm()
    if form.validate_on_submit():
        skill = form.skill_title.data.strip()
        level = form.target_level.data
        
        plan_data = AIService.generate_roadmap(skill, level, user_id=current_user.id)
        
        roadmap = LearningRoadmap(
            user_id=current_user.id,
            skill_title=skill,
            target_level=level,
            summary=plan_data.get("description", ""),
            plan_json=json.dumps(plan_data),
        )
        db.session.add(roadmap)
        db.session.flush()

        # Initialize progress items for all topics
        for week in plan_data.get("weeks", []):
            for t in week.get("topics", []):
                p = RoadmapProgress(
                    roadmap_id=roadmap.id,
                    item_key=t.get("key", f"w{week.get('week_number')}_{t.get('title')[:10]}"),
                    title=t.get("title", ""),
                    done=False,
                )
                db.session.add(p)

        db.session.commit()
        flash(f"Generated new AI learning roadmap for '{skill}'!", "success")
        return redirect(url_for("ai.roadmap_detail", roadmap_id=roadmap.id))

    user_roadmaps = (
        LearningRoadmap.query.filter_by(user_id=current_user.id)
        .order_by(LearningRoadmap.created_at.desc())
        .all()
    )
    return render_template("ai/roadmap_list.html", form=form, roadmaps=user_roadmaps)


@bp.route("/roadmap/<int:roadmap_id>")
@login_required
def roadmap_detail(roadmap_id):
    roadmap = LearningRoadmap.query.get_or_404(roadmap_id)
    if roadmap.user_id != current_user.id and not current_user.is_admin:
        flash("You do not have permission to view this roadmap.", "danger")
        return redirect(url_for("ai.roadmap_index"))

    progress_map = {p.item_key: p.done for p in roadmap.progress_items}
    return render_template("ai/roadmap_detail.html", roadmap=roadmap, progress_map=progress_map)


@bp.route("/roadmap/<int:roadmap_id>/toggle/<item_key>", methods=["POST"])
@login_required
def roadmap_toggle(roadmap_id, item_key):
    roadmap = LearningRoadmap.query.get_or_404(roadmap_id)
    if roadmap.user_id != current_user.id:
        return jsonify(error="Unauthorized"), 403

    prog = RoadmapProgress.query.filter_by(roadmap_id=roadmap.id, item_key=item_key).first()
    if not prog:
        prog = RoadmapProgress(roadmap_id=roadmap.id, item_key=item_key, done=True, completed_at=datetime.now(timezone.utc))
        db.session.add(prog)
    else:
        prog.done = not prog.done
        prog.completed_at = datetime.now(timezone.utc) if prog.done else None

    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            success=True,
            done=prog.done,
            completion_percentage=roadmap.completion_percentage,
        )

    return redirect(url_for("ai.roadmap_detail", roadmap_id=roadmap.id))


@bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz_index():
    form = QuizRequestForm()
    if form.validate_on_submit():
        skill = form.skill_title.data.strip()
        difficulty = form.difficulty.data

        questions = AIService.generate_quiz(skill, difficulty, user_id=current_user.id)
        
        quiz = GeneratedQuiz(
            user_id=current_user.id,
            skill_title=skill,
            difficulty=difficulty,
            questions_json=json.dumps(questions),
        )
        db.session.add(quiz)
        db.session.commit()

        flash(f"Quiz ready! Complete the 5 questions to test your knowledge in '{skill}'.", "success")
        return redirect(url_for("ai.quiz_take", quiz_id=quiz.id))

    user_quizzes = (
        GeneratedQuiz.query.filter_by(user_id=current_user.id)
        .order_by(GeneratedQuiz.created_at.desc())
        .all()
    )
    return render_template("ai/quiz_list.html", form=form, quizzes=user_quizzes)


@bp.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def quiz_take(quiz_id):
    quiz = GeneratedQuiz.query.get_or_404(quiz_id)
    questions = quiz.parsed_questions

    latest_attempt = (
        QuizAttempt.query.filter_by(quiz_id=quiz.id, user_id=current_user.id)
        .order_by(QuizAttempt.attempted_at.desc())
        .first()
    )

    if request.method == "POST":
        user_answers = {}
        score = 0
        total = len(questions)

        for i, q in enumerate(questions):
            selected = request.form.get(f"q_{i}", type=int)
            user_answers[str(i)] = selected
            if selected is not None and selected == q.get("correct_index"):
                score += 1

        passed = score >= (total * 0.6)  # 60% or higher to pass

        attempt = QuizAttempt(
            quiz_id=quiz.id,
            user_id=current_user.id,
            score=score,
            total_questions=total,
            passed=passed,
            answers_json=json.dumps(user_answers),
        )
        db.session.add(attempt)
        db.session.commit()

        if passed:
            flash(f"Congratulations! You scored {score}/{total} ({attempt.percentage}%) and earned your badge!", "success")
        else:
            flash(f"You scored {score}/{total} ({attempt.percentage}%). Review the answers below to reinforce your knowledge.", "info")

        return render_template(
            "ai/quiz_result.html",
            quiz=quiz,
            questions=questions,
            attempt=attempt,
            user_answers=user_answers,
        )

    # If already taken and viewing result
    if latest_attempt and request.args.get("view_result") == "1":
        return render_template(
            "ai/quiz_result.html",
            quiz=quiz,
            questions=questions,
            attempt=latest_attempt,
            user_answers=latest_attempt.parsed_answers,
        )

    # Sanitized questions for client (answers hidden)
    client_questions = quiz.questions_for_client
    return render_template("ai/quiz_take.html", quiz=quiz, questions=client_questions, latest_attempt=latest_attempt)


@bp.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant():
    # Retrieve or create active conversation
    conv = (
        AIConversation.query.filter_by(user_id=current_user.id)
        .order_by(AIConversation.created_at.desc())
        .first()
    )
    if not conv:
        conv = AIConversation(user_id=current_user.id, title="Learning & Swap Advice")
        db.session.add(conv)
        db.session.commit()

    if request.method == "POST":
        user_text = request.form.get("message", "").strip()
        if user_text:
            user_msg = AIMessage(conversation_id=conv.id, role="user", content=user_text)
            db.session.add(user_msg)
            db.session.flush()

            # Prepare history for AI
            history = [
                {"role": m.role, "content": m.content}
                for m in conv.messages[-8:]
            ]

            assistant_reply = AIService.generate_assistant_reply(history, user_id=current_user.id)
            bot_msg = AIMessage(conversation_id=conv.id, role="assistant", content=assistant_reply)
            db.session.add(bot_msg)
            db.session.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(reply=assistant_reply)

        return redirect(url_for("ai.assistant"))

    return render_template("ai/assistant.html", conversation=conv)


@bp.route("/assistant/clear", methods=["POST"])
@login_required
def assistant_clear():
    AIConversation.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Chat history cleared.", "info")
    return redirect(url_for("ai.assistant"))
