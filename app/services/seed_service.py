from datetime import datetime, timezone, timedelta
from decimal import Decimal
from app.extensions import db
from app.models.user import User
from app.models.skills import SkillCategory, Skill, UserSkill, AvailabilitySlot
from app.models.wallet import Wallet, WalletTransaction, CreditReservation
from app.models.booking import Booking
from app.models.review import Review
from app.models.notification import Notification
from app.models.ai import LearningRoadmap, RoadmapProgress, GeneratedQuiz
from app.services.wallet_service import add_bonus_credits, get_or_create_wallet
from app.services.ai_service import AIService


def seed_database():
    """Populates realistic demo data for college examination & demonstration."""
    # 1. Categories
    categories_data = [
        {"name": "Programming & Technology", "icon": "bi-code-slash", "description": "Software development, web design, databases, and algorithms"},
        {"name": "Design & Creative Arts", "icon": "bi-palette", "description": "UI/UX, visual design, Figma, illustration, and branding"},
        {"name": "Languages & Communication", "icon": "bi-translate", "description": "Conversational practice, pronunciation, and vocabulary"},
        {"name": "Business & Career", "icon": "bi-briefcase", "description": "Data analysis, spreadsheets, marketing, and interview coaching"},
        {"name": "Music & Audio", "icon": "bi-music-note-beamed", "description": "Instrument lessons, vocal training, and audio production"},
        {"name": "Academics & Science", "icon": "bi-book", "description": "Mathematics, physics, statistics, and test prep"},
    ]

    cat_map = {}
    for c_info in categories_data:
        cat = SkillCategory.query.filter_by(name=c_info["name"]).first()
        if not cat:
            cat = SkillCategory(**c_info)
            db.session.add(cat)
            db.session.flush()
        cat_map[c_info["name"]] = cat

    # 2. Skills
    skills_data = [
        ("Programming & Technology", "Python Programming"),
        ("Programming & Technology", "JavaScript & React"),
        ("Programming & Technology", "Flask & Backend Architecture"),
        ("Design & Creative Arts", "UI/UX Design in Figma"),
        ("Design & Creative Arts", "Graphic Design & Branding"),
        ("Languages & Communication", "Spanish Conversation"),
        ("Languages & Communication", "Public Speaking & Pitching"),
        ("Business & Career", "Data Analysis with Excel"),
        ("Business & Career", "Digital Marketing Strategy"),
        ("Music & Audio", "Acoustic Guitar Basics"),
    ]

    skill_map = {}
    for cat_name, skill_name in skills_data:
        cat = cat_map[cat_name]
        sk = Skill.query.filter_by(category_id=cat.id, name=skill_name).first()
        if not sk:
            sk = Skill(category_id=cat.id, name=skill_name)
            db.session.add(sk)
            db.session.flush()
        skill_map[skill_name] = sk

    # 3. Users
    users_data = [
        {
            "username": "admin",
            "email": "admin@skillswap.com",
            "password": "AdminPass123!",
            "full_name": "System Administrator",
            "role": "admin",
            "headline": "SkillSwap Platform Supervisor",
            "location": "Global / Remote",
            "bio": "Managing platform integrity, dispute mediation, and credit distribution audits.",
        },
        {
            "username": "alex_dev",
            "email": "alex@skillswap.com",
            "password": "UserPass123!",
            "full_name": "Alex Rivera",
            "role": "user",
            "headline": "Full-Stack Software Engineer & Python Tutor",
            "location": "San Francisco, CA",
            "bio": "Passionate backend engineer with 3+ years writing Python and web services. Excited to teach coding and learn UI/UX design and Figma!",
        },
        {
            "username": "sarah_ui",
            "email": "sarah@skillswap.com",
            "password": "UserPass123!",
            "full_name": "Sarah Chen",
            "role": "user",
            "headline": "Product Designer & Figma Specialist",
            "location": "Seattle, WA",
            "bio": "Lead UI/UX designer. I teach design systems, user journey mapping, and prototyping in Figma. Looking to learn Excel & data analysis!",
        },
        {
            "username": "marcus_data",
            "email": "marcus@skillswap.com",
            "password": "UserPass123!",
            "full_name": "Marcus Vance",
            "role": "user",
            "headline": "Financial Analyst & Advanced Excel Specialist",
            "location": "New York, NY",
            "bio": "Financial analyst passionate about pivot tables, XLOOKUP, and financial modeling. Eager to learn Python to automate workflows!",
        },
        {
            "username": "elena_polyglot",
            "email": "elena@skillswap.com",
            "password": "UserPass123!",
            "full_name": "Elena Rostova",
            "role": "user",
            "headline": "Native Spanish & Multilingual Coach",
            "location": "Austin, TX",
            "bio": "Language enthusiast. I run interactive conversational sessions to get you speaking fluently. Looking to learn graphic design!",
        },
        {
            "username": "david_music",
            "email": "david@skillswap.com",
            "password": "UserPass123!",
            "full_name": "David Kim",
            "role": "user",
            "headline": "Acoustic Guitarist & Audio Creator",
            "location": "Chicago, IL",
            "bio": "Fingerstyle guitar enthusiast and music producer. Happy to teach chords, rhythm, and song crafting in exchange for web tech!",
        },
    ]

    user_map = {}
    for u_info in users_data:
        pwd = u_info.pop("password")
        u = User.query.filter_by(username=u_info["username"]).first()
        if not u:
            u = User(**u_info)
            u.set_password(pwd)
            db.session.add(u)
            db.session.flush()
            
            # Setup wallet with bonus
            wallet = get_or_create_wallet(u.id)
            wallet.available_balance = Decimal("4.00")
            add_bonus_credits(u.id, Decimal("4.00"), description="Platform welcome grant")
        user_map[u.username] = u

    # 4. User Skills (Offers & Wants)
    alex = user_map["alex_dev"]
    sarah = user_map["sarah_ui"]
    marcus = user_map["marcus_data"]
    elena = user_map["elena_polyglot"]
    david = user_map["david_music"]

    user_skills_setup = [
        # Alex offers Python, wants Figma
        (alex, "Python Programming", "offer", "Advanced", 60, "Complete hands-on Python from syntax to functions, APIs, and mini-projects."),
        (alex, "UI/UX Design in Figma", "want", "Beginner", 60, "Want to learn wireframing, component design, and Figma shortcuts."),
        # Sarah offers Figma, wants Excel
        (sarah, "UI/UX Design in Figma", "offer", "Expert", 60, "Interactive Figma masterclass: auto-layout, design tokens, responsive grids."),
        (sarah, "Data Analysis with Excel", "want", "Beginner", 60, "Need practical training on formulas, dashboards, and pivot tables."),
        # Marcus offers Excel, wants Python
        (marcus, "Data Analysis with Excel", "offer", "Expert", 60, "From messy data to automated financial dashboards and macros."),
        (marcus, "Python Programming", "want", "Intermediate", 60, "Learning Pandas and requests library for automated reports."),
        # Elena offers Spanish, wants Graphic Design
        (elena, "Spanish Conversation", "offer", "Expert", 30, "Fun conversational drills covering idioms, travel phrasing, and pronunciation."),
        (elena, "Graphic Design & Branding", "want", "Beginner", 60, "Learning logo creation, typography, and Canva/Photoshop assets."),
        # David offers Guitar, wants JavaScript
        (david, "Acoustic Guitar Basics", "offer", "Intermediate", 60, "Learn your first 5 chord progressions and fingerpicking techniques."),
        (david, "JavaScript & React", "want", "Beginner", 60, "Building an interactive portfolio website."),
    ]

    for usr, sk_name, kind, lvl, mins, desc in user_skills_setup:
        sk = skill_map[sk_name]
        us = UserSkill.query.filter_by(user_id=usr.id, skill_id=sk.id, kind=kind).first()
        if not us:
            us = UserSkill(
                user_id=usr.id,
                skill_id=sk.id,
                kind=kind,
                level=lvl,
                session_minutes=mins,
                description=desc,
                is_active=True,
            )
            db.session.add(us)

    db.session.commit()

    # 5. Sample Bookings
    now = datetime.now(timezone.utc)

    # Past completed booking: Alex taught Marcus Python
    b1 = Booking.query.filter_by(learner_id=marcus.id, teacher_id=alex.id).first()
    if not b1:
        b1 = Booking(
            learner_id=marcus.id,
            teacher_id=alex.id,
            skill_id=skill_map["Python Programming"].id,
            start_utc=now - timedelta(days=2),
            duration_min=60,
            credits=Decimal("1.00"),
            status="completed",
            room_id="skillswap-demo-session-101",
            learner_confirmed=True,
            teacher_confirmed=True,
            notes="Marcus wants to learn how to read CSV files and automate data manipulation with Python scripts.",
        )
        db.session.add(b1)
        db.session.flush()

        # Review from Marcus to Alex
        rev = Review(
            booking_id=b1.id,
            reviewer_id=marcus.id,
            reviewee_id=alex.id,
            rating=5,
            comment="Alex was an incredible mentor! In just one hour we wrote a Python script that automated my 30-minute daily Excel task. Clear explanations and very patient.",
        )
        db.session.add(rev)

    # Upcoming scheduled booking: Sarah teaching Alex Figma tomorrow
    b2 = Booking.query.filter_by(learner_id=alex.id, teacher_id=sarah.id).first()
    if not b2:
        b2 = Booking(
            learner_id=alex.id,
            teacher_id=sarah.id,
            skill_id=skill_map["UI/UX Design in Figma"].id,
            start_utc=now + timedelta(hours=3),
            duration_min=60,
            credits=Decimal("1.00"),
            status="scheduled",
            room_id="skillswap-demo-session-102",
            notes="Reviewing auto-layout and setting up a basic mobile application design system.",
        )
        db.session.add(b2)
        db.session.flush()

        # Reservation for booking 2
        res = CreditReservation(
            booking_id=b2.id,
            learner_id=alex.id,
            amount=Decimal("1.00"),
            status="held",
        )
        db.session.add(res)

    # 6. Sample AI Roadmap for Alex
    rm = LearningRoadmap.query.filter_by(user_id=alex.id).first()
    if not rm:
        rm_data = AIService.generate_roadmap("UI/UX Design in Figma", "Beginner", user_id=alex.id)
        import json
        rm = LearningRoadmap(
            user_id=alex.id,
            skill_title="UI/UX Design in Figma",
            target_level="Beginner",
            summary=rm_data.get("description", ""),
            plan_json=json.dumps(rm_data),
        )
        db.session.add(rm)
        db.session.flush()

        for week in rm_data.get("weeks", []):
            for t in week.get("topics", []):
                p = RoadmapProgress(
                    roadmap_id=rm.id,
                    item_key=t.get("key", f"w{week.get('week_number')}_{t.get('title')[:10]}"),
                    title=t.get("title", ""),
                    done=(week.get("week_number") == 1),  # mark week 1 as done for demo!
                )
                db.session.add(p)

    # 7. Notifications
    Notification.query.filter_by(user_id=alex.id).delete()
    notifs = [
        Notification(
            user_id=alex.id,
            type="booking_accepted",
            title="Session Confirmed! 🎉",
            message="Sarah Chen accepted your UI/UX Design session for today.",
            link=f"/bookings/{b2.id if b2 else 1}",
        ),
        Notification(
            user_id=alex.id,
            type="review_received",
            title="New 5-Star Review! ⭐",
            message="Marcus Vance left you a glowing 5★ review for Python Programming.",
            link="/profile/alex_dev",
        ),
    ]
    for n in notifs:
        db.session.add(n)

    db.session.commit()
    print("Database successfully seeded with demo data!")
