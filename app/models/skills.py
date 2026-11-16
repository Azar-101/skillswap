from datetime import datetime, timezone
from app.extensions import db


class SkillCategory(db.Model):
    __tablename__ = "skill_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), default="")
    icon = db.Column(db.String(64), default="bi-mortarboard")

    skills = db.relationship("Skill", back_populates="category", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"<SkillCategory {self.name}>"


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("skill_categories.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)

    category = db.relationship("SkillCategory", back_populates="skills")
    user_skills = db.relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan", lazy="dynamic")
    bookings = db.relationship("Booking", back_populates="skill", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("category_id", "name", name="uq_category_skill_name"),
    )

    def __repr__(self):
        return f"<Skill {self.name}>"


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, index=True)
    kind = db.Column(db.String(10), default="offer", nullable=False)  # 'offer' or 'want'
    level = db.Column(db.String(20), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced, Expert
    description = db.Column(db.Text, default="")
    session_minutes = db.Column(db.Integer, default=60, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    @property
    def credit_cost(self) -> float:
        # Time-based: 60m = 1.0, 30m = 0.5, 90m = 1.5, 120m = 2.0
        return round(self.session_minutes / 60.0, 2)

    def __repr__(self):
        return f"<UserSkill user_id={self.user_id} skill_id={self.skill_id} kind={self.kind}>"


class AvailabilitySlot(db.Model):
    __tablename__ = "availability_slots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday ... 6=Sunday
    start_time = db.Column(db.String(10), nullable=False)  # "09:00"
    end_time = db.Column(db.String(10), nullable=False)    # "17:00"
    tz = db.Column(db.String(50), default="UTC")

    user = db.relationship("User", back_populates="availability")

    WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @property
    def weekday_name(self):
        if 0 <= self.weekday <= 6:
            return self.WEEKDAY_NAMES[self.weekday]
        return "Unknown"
