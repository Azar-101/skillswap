from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    email = StringField("Email Address or Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField("Email Address", validators=[DataRequired(), Email(check_deliverability=False, message="Please provide a valid email address.")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    headline = StringField("Headline (e.g. CS Student | Python Enthusiast)", validators=[Length(max=150)])
    submit = SubmitField("Create Free Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError("This username is already taken. Please choose another.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("An account with this email already exists.")


class ProfileEditForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    headline = StringField("Headline", validators=[Length(max=150)])
    location = StringField("Location", validators=[Length(max=100)])
    timezone = StringField("Timezone", validators=[Length(max=50)])
    bio = TextAreaField("Bio & Learning Interests", validators=[Length(max=1000)])
    submit = SubmitField("Save Profile")
