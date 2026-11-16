from datetime import datetime, timezone
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class BookingRequestForm(FlaskForm):
    start_time = DateTimeLocalField(
        "Preferred Date & Time",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
    )
    duration_min = SelectField(
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
    notes = TextAreaField(
        "Message to Teacher / Learning Goals",
        validators=[Length(max=500)],
        render_kw={"placeholder": "Introduce yourself and mention what you hope to cover during this session..."},
    )
    submit = SubmitField("Send Swap Request")

    def validate_start_time(self, field):
        if field.data:
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            if field.data < now_naive:
                raise ValidationError("Session start time must be in the future.")


class DisputeForm(FlaskForm):
    reason = TextAreaField(
        "Reason for Dispute",
        validators=[DataRequired(), Length(min=10, max=1000)],
        render_kw={"placeholder": "Describe what occurred (e.g. participant was absent, technical breakdown, incorrect topic)..."},
    )
    submit = SubmitField("Submit Dispute to Admin")
