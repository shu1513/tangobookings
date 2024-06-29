import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flaskblog import mail
from flask import current_app


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, "static/profile_pics", picture_file_name
    )
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return picture_file_name


def remove_old_picture(old_pic):
    if old_pic != "default.png":
        os.remove(os.path.join(current_app.root_path, "static/profile_pics", old_pic))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="shu151343@gmail.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did NOT make the request please ignore this email.
    """
    mail.send(msg)


def send_verify_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Email Verification", sender="shu151343@gmail.com", recipients=[user.email]
    )
    msg.body = f"""To complete your registration, please verify your email by visit the following link:
{url_for('users.verify_token', token=token, _external=True)}
If you did NOT make the request please ignore this email.
    """
    mail.send(msg)
