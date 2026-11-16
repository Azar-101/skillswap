from app.models.user import User
from app.models.skills import UserSkill, Skill


def find_matches_for_user(user: User, limit: int = 10) -> list:
    """Computes smart match scores between the user's wanted skills and all community offers."""
    wanted_skills = user.skills.filter_by(kind="want", is_active=True).all()
    offered_by_user = {us.skill.name.lower(): us for us in user.skills.filter_by(kind="offer", is_active=True).all()}
    
    # All candidate offers from other active users
    candidates = (
        UserSkill.query.filter(
            UserSkill.kind == "offer",
            UserSkill.is_active.is_(True),
            UserSkill.user_id != user.id,
        )
        .all()
    )

    scored_matches = []

    wanted_names = [w.skill.name.lower() for w in wanted_skills]
    wanted_cat_ids = [w.skill.category_id for w in wanted_skills]

    for cand in candidates:
        teacher = cand.user
        if not teacher or teacher.status != "active":
            continue

        cand_skill_name = cand.skill.name.lower()
        score = 40  # base compatibility
        factors = []

        # 1. Direct or partial skill name match
        matched_wanted = None
        for w in wanted_skills:
            w_name = w.skill.name.lower()
            if w_name == cand_skill_name:
                score += 35
                factors.append(f"Direct match for '{w.skill.name}'")
                matched_wanted = w
                break
            elif w_name in cand_skill_name or cand_skill_name in w_name:
                score += 25
                factors.append(f"Related match for '{w.skill.name}'")
                matched_wanted = w
                break

        # 2. Category match if no direct match
        if not matched_wanted and cand.skill.category_id in wanted_cat_ids:
            score += 15
            factors.append(f"In your target learning category ({cand.skill.category.name})")

        # 3. Rating & Experience fit
        rating = teacher.average_rating
        if rating >= 4.5:
            score += 15
            factors.append(f"Top-rated teacher ({rating}★)")
        elif rating >= 4.0:
            score += 10
            factors.append(f"Well-rated teacher ({rating}★)")

        # 4. Reciprocal swap potential (Does teacher want what current user offers?)
        teacher_wants = [tw.skill.name.lower() for tw in teacher.skills.filter_by(kind="want", is_active=True).all()]
        reciprocal_skills = [s for s in teacher_wants if s in offered_by_user]
        if reciprocal_skills:
            score += 15
            factors.append(f"Direct swap potential: They want to learn your skill '{reciprocal_skills[0].title()}'!")

        # 5. Level fit
        if cand.level in ("Advanced", "Expert"):
            score += 5
            factors.append(f"Expert instructor level ({cand.level})")

        normalized_score = min(99, max(45, score))

        explanation = " • ".join(factors) if factors else "Community member teaching in-demand topics"

        scored_matches.append({
            "user_skill": cand,
            "teacher": teacher,
            "skill": cand.skill,
            "score": normalized_score,
            "explanation": explanation,
            "has_reciprocal": len(reciprocal_skills) > 0,
            "reciprocal_skill": reciprocal_skills[0].title() if reciprocal_skills else None,
        })

    # Sort descending by score
    scored_matches.sort(key=lambda m: m["score"], reverse=True)
    return scored_matches[:limit]
