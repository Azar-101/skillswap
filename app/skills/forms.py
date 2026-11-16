from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class UserSkillForm(FlaskForm):
    category_id = SelectField("Skill Category", coerce=int, validators=[DataRequired()])
    skill_name = StringField("Skill Name (e.g. Python, Graphic Design, Public Speaking)", validators=[DataRequired(), Length(min=2, max=100)])
    kind = SelectField(
        "Type of Listing",
        choices=[("offer", "I want to TEACH this skill (Earn Credits)"), ("want", "I want to LEARN this skill (Spend Credits)")],
        validators=[DataRequired()],
    )
    level = SelectField(
        "Skill Level",
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
            ("Expert", "Expert"),
        ],
        default="Intermediate",
    )
    session_minutes = SelectField(
        "Session Duration",
        coerce=int,
        choices=[
            (30, "30 minutes (0.5 Credits)"),
            (60, "60 minutes (1.0 Credit)"),
            (90, "90 minutes (1.5 Credits)"),
            (120, "120 minutes (2.0 Credits)"),
        ],
        default=60,
    )
    description = TextAreaField(
        "Description & What You'll Cover",
        validators=[Length(max=1000)],
        render_kw={"placeholder": "Share what you'll teach, topics, prerequisites, or specific questions you need help with..."},
    )
    submit = SubmitField("Save Skill Listing")
