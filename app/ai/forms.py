from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class RoadmapRequestForm(FlaskForm):
    skill_title = StringField(
        "Skill or Topic to Master",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "e.g. Python for Data Science, Figma UI Design, Docker & Kubernetes..."},
    )
    target_level = SelectField(
        "Target Proficiency",
        choices=[
            ("Beginner", "Beginner (Zero to Fundamentals)"),
            ("Intermediate", "Intermediate (Practical & Projects)"),
            ("Advanced", "Advanced (Optimization & Production Architecture)"),
        ],
        default="Intermediate",
    )
    submit = SubmitField("Generate 4-Week AI Roadmap")


class QuizRequestForm(FlaskForm):
    skill_title = StringField(
        "Topic / Skill",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "e.g. JavaScript Async/Await, SQL Optimization, Git Workflows..."},
    )
    difficulty = SelectField(
        "Assessment Difficulty",
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ],
        default="Intermediate",
    )
    submit = SubmitField("Generate Skill Quiz")
