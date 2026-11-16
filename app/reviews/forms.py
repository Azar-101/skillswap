from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class ReviewForm(FlaskForm):
    rating = SelectField(
        "Rating (1 to 5 Stars)",
        coerce=int,
        choices=[
            (5, "⭐⭐⭐⭐⭐ 5 Stars - Outstanding & Inspiring"),
            (4, "⭐⭐⭐⭐ 4 Stars - Very Helpful & Knowledgeable"),
            (3, "⭐⭐⭐ 3 Stars - Good & As Described"),
            (2, "⭐⭐ 2 Stars - Fair, Needs Improvement"),
            (1, "⭐ 1 Star - Unsatisfactory"),
        ],
        default=5,
        validators=[DataRequired()],
    )
    comment = TextAreaField(
        "Written Review & Feedback",
        validators=[DataRequired(), Length(min=5, max=1000)],
        render_kw={"placeholder": "Share your experience with this peer teacher: communication, clarity, practical knowledge..."},
    )
    submit = SubmitField("Submit Review")
