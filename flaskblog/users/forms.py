import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    RadioField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import User

# ROLE_CHOICES is for both RegistrationForm and UpdateAccountForm
ROLE_CHOICES = [("Follower", "Follower"), ("Leader", "Leader"), ("Both", "Both")]


# Function to validate role field
def validate_role(form, field):
    valid_roles = [choice[0] for choice in ROLE_CHOICES]
    if field.data not in valid_roles:
        raise ValidationError("Please select a valid role from above.")


# set password criteria
def password_complexity_check(form, field):
    password = field.data
    if (
        len(password) < 8
        or len(password) > 16
        or not re.search(r"[A-Z]", password)
        or not re.search(r"[a-z]", password)
        or not re.search(r"[0-9]", password)
        or not re.search(r"[!@#$%^&*(),.?\":{}|<>-]", password)
    ):
        raise ValidationError(
            "Password must be 8-16 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character."
        )


# set name crteria
def name_check(form, field):
    name = field.data
    if not re.match("^[A-Za-z]+$", name):
        raise ValidationError("Can not contain numbers, spaces, or special characters.")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username:", validators=[DataRequired(), Length(min=4, max=20)]
    )
    email = StringField("Email:", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password:",
        validators=[DataRequired(), Length(min=8, max=16), password_complexity_check],
    )
    confirm_password = PasswordField(
        "Confirm Password:", validators=[DataRequired(), EqualTo("password")]
    )
    first_name = StringField(
        "First Name:", validators=[DataRequired(), Length(max=25), name_check]
    )
    last_name = StringField(
        "Last Name:", validators=[DataRequired(), Length(max=25), name_check]
    )
    role = RadioField(
        "Role:",
        choices=ROLE_CHOICES,
        validators=[DataRequired(), validate_role],
    )
    submit = SubmitField("Sign Up")

    # make sure username entered is not already in the data base
    def validate_username(form, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken, please choose another")

    # make sure email entered is not already in the data base
    def validate_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("email already taken, please choose another")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username:", validators=[DataRequired(), Length(min=4, max=20)]
    )
    email = StringField("Email:", validators=[DataRequired(), Email()])
    first_name = StringField(
        "First Name:", validators=[DataRequired(), Length(max=25), name_check]
    )
    last_name = StringField(
        "Last Name:", validators=[DataRequired(), Length(max=25), name_check]
    )
    role = RadioField(
        "Role:",
        choices=ROLE_CHOICES,
        validators=[DataRequired(), validate_role],
    )

    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png", "jpeg"])]
    )
    submit = SubmitField("update")

    # make sure username entered is not already in the data base unless it is the current user's username
    def validate_username(form, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username already taken, please choose another")

    # make sure email entered is not already in the data base unless it is the current user's email
    def validate_email(form, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("email already taken, please choose another")


class RequestResetForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    # I omit the following funciton for security, to avoid enumeration attack.
    """def validate_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "If an account with this email address exists, a password reset message will be sent shortly"
            )"""


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password:",
        validators=[DataRequired(), Length(min=8, max=16), password_complexity_check],
    )
    confirm_password = PasswordField(
        "Confirm Password:", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
