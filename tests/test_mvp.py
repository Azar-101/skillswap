from decimal import Decimal
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models.user import User
from app.models.skills import SkillCategory, Skill, UserSkill
from app.models.wallet import Wallet, WalletTransaction, CreditReservation
from app.models.booking import Booking
from app.models.review import Review
from app.services.wallet_service import (
    calculate_credits_for_duration,
    get_or_create_wallet,
    add_bonus_credits,
    reserve_credits,
    release_credits,
    transfer_credits_on_completion,
)
from app.services.booking_service import (
    create_booking_request,
    accept_booking,
    confirm_booking_completion,
    open_booking_dispute,
)
from app.services.matching_service import find_matches_for_user
from app.services.ai_service import AIService


def test_credit_duration_calculation():
    assert calculate_credits_for_duration(30) == Decimal("0.50")
    assert calculate_credits_for_duration(60) == Decimal("1.00")
    assert calculate_credits_for_duration(90) == Decimal("1.50")
    assert calculate_credits_for_duration(120) == Decimal("2.00")


def test_user_wallet_and_bonus(app):
    with app.app_context():
        user = User(
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
        )
        user.set_password("Secret123!")
        db.session.add(user)
        db.session.commit()

        wallet = get_or_create_wallet(user.id)
        assert wallet is not None
        assert wallet.available_balance == Decimal("0.00")

        # Add bonus
        add_bonus_credits(user.id, Decimal("2.00"), "Signup bonus")
        assert wallet.available_balance == Decimal("2.00")
        assert wallet.reserved_balance == Decimal("0.00")
        assert wallet.total_balance == Decimal("2.00")


def test_booking_and_escrow_lifecycle(app):
    with app.app_context():
        cat = SkillCategory(name="Tech", icon="bi-code")
        db.session.add(cat)
        db.session.flush()

        skill = Skill(category_id=cat.id, name="Python Programming")
        db.session.add(skill)
        db.session.flush()

        # Learner
        learner = User(username="learner1", email="learner1@example.com", full_name="Learner One")
        learner.set_password("Pass123!")
        db.session.add(learner)

        # Teacher
        teacher = User(username="teacher1", email="teacher1@example.com", full_name="Teacher One")
        teacher.set_password("Pass123!")
        db.session.add(teacher)
        db.session.commit()

        # Setup wallets: learner has 2 credits, teacher has 0
        get_or_create_wallet(learner.id)
        add_bonus_credits(learner.id, Decimal("2.00"))
        get_or_create_wallet(teacher.id)

        # 1. Learner requests booking (60 mins = 1 credit)
        now = datetime.now(timezone.utc)
        booking = create_booking_request(
            learner_id=learner.id,
            teacher_id=teacher.id,
            skill_id=skill.id,
            start_utc=now + timedelta(days=1),
            duration_min=60,
            notes="Need help with loops",
        )
        assert booking.status == "pending"
        assert booking.credits == Decimal("1.00")
        # Credits are NOT yet locked while pending
        l_wallet = get_or_create_wallet(learner.id)
        assert l_wallet.available_balance == Decimal("2.00")
        assert l_wallet.reserved_balance == Decimal("0.00")

        # 2. Teacher accepts booking -> Credits move from available to reserved escrow
        accept_booking(booking.id, teacher.id)
        assert booking.status == "scheduled"
        assert l_wallet.available_balance == Decimal("1.00")
        assert l_wallet.reserved_balance == Decimal("1.00")

        # 3. Session finishes -> Complete booking and release escrow to teacher
        confirm_booking_completion(booking.id, learner.id)
        assert booking.status == "completed"

        t_wallet = get_or_create_wallet(teacher.id)
        assert l_wallet.reserved_balance == Decimal("0.00")
        assert l_wallet.available_balance == Decimal("1.00")
        assert t_wallet.available_balance == Decimal("1.00")


def test_ai_matching(app):
    with app.app_context():
        cat = SkillCategory.query.first() or SkillCategory(name="Coding")
        db.session.add(cat)
        db.session.flush()

        s_py = Skill(category_id=cat.id, name="Python Web")
        s_fig = Skill(category_id=cat.id, name="Figma Prototyping")
        db.session.add_all([s_py, s_fig])
        db.session.commit()

        u_alice = User(username="alice", email="alice@test.com", full_name="Alice")
        u_alice.set_password("Pass123!")
        u_bob = User(username="bob", email="bob@test.com", full_name="Bob")
        u_bob.set_password("Pass123!")
        db.session.add_all([u_alice, u_bob])
        db.session.commit()

        # Alice wants Python, offers Figma
        db.session.add(UserSkill(user_id=u_alice.id, skill_id=s_py.id, kind="want", level="Beginner"))
        db.session.add(UserSkill(user_id=u_alice.id, skill_id=s_fig.id, kind="offer", level="Expert"))

        # Bob offers Python, wants Figma (Reciprocal match!)
        db.session.add(UserSkill(user_id=u_bob.id, skill_id=s_py.id, kind="offer", level="Advanced"))
        db.session.add(UserSkill(user_id=u_bob.id, skill_id=s_fig.id, kind="want", level="Beginner"))
        db.session.commit()

        matches = find_matches_for_user(u_alice)
        assert len(matches) > 0
        top_match = matches[0]
        assert top_match["teacher"].id == u_bob.id
        assert top_match["has_reciprocal"] is True
        assert top_match["score"] >= 80


def test_ai_roadmap_generation(app):
    with app.app_context():
        roadmap = AIService.generate_roadmap("Docker Containerization", "Intermediate")
        assert "weeks" in roadmap
        assert len(roadmap["weeks"]) == 4
        week1 = roadmap["weeks"][0]
        assert "theme" in week1
        assert "topics" in week1
        assert len(week1["topics"]) > 0


def test_ai_quiz_generation(app):
    with app.app_context():
        quiz = AIService.generate_quiz("SQL Indexing", "Advanced")
        assert isinstance(quiz, list)
        assert len(quiz) == 5
        q1 = quiz[0]
        assert "question" in q1
        assert "options" in q1
        assert len(q1["options"]) == 4
        assert "correct_index" in q1
        assert "explanation" in q1


def test_landing_page_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "SkillSwap" in r.get_data(as_text=True)
    assert "Exchange Skills" in r.get_data(as_text=True)


def test_marketplace_page_renders(client):
    r = client.get("/skills/")
    assert r.status_code == 200
    assert "Skill Marketplace" in r.get_data(as_text=True)


def test_dashboard_renders_for_logged_in_user(client, app):
    with app.app_context():
        u = User.query.filter_by(username="alex_dev").first()
        if not u:
            u = User(username="alex_dev", email="alex@skillswap.com", full_name="Alex Rivera")
            u.set_password("UserPass123!")
            db.session.add(u)
            db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
        sess["_fresh"] = True
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Welcome back" in r.get_data(as_text=True)
