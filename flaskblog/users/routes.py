import os
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    Blueprint,
)
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)
from flaskblog.users.utils import (
    save_picture,
    remove_old_picture,
    send_reset_email,
    send_verify_email,
)

users = Blueprint("users", __name__, template_folder="templates")


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
        )
        db.session.add(user)
        db.session.commit()
        send_verify_email(user)
        flash(
            f"{form.first_name.data}, a verification email has been sent to your inbox. Please check your email to complete the registration process. In case you do not see the verification email in your inbox, please also check your spam folder.",
            "success",
        )
        return redirect(url_for("users.login"))
    return render_template("users/register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (
            user
            and bcrypt.check_password_hash(user.password, form.password.data)
            and user.email_verified
        ):
            login_user(user, remember=form.remember.data)
            flash(f"You are logged in.", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        elif (
            user
            and bcrypt.check_password_hash(user.password, form.password.data)
            and not user.email_verified
        ):
            flash(
                "Please verify your email in your inbox and then login again", "danger"
            )
        else:
            flash("Login unsuccessful. Please check email and password", "danger")
    return render_template("users/login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    flash(f"logged out!", "success")
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_pic = current_user.image_file
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            remove_old_picture(old_pic)

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.role = form.role.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.role.data = current_user.role
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "users/account.html", title="Account", image_file=image_file, form=form
    )


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=7)
    )
    return render_template("users/user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash(
            "If an account with this email address exists, a password reset message will be sent shortly. Please check your spam folder as well",
            "info",
        )
        return redirect(url_for("users.login"))
    return render_template(
        "users/reset_request.html", title="Reset Password", form=form
    )


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_token(token)
    if user is None:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash(
            f"{user.first_name} your password has been updated!",
            "success",
        )
        return redirect(url_for("users.login"))
    return render_template("users/reset_token.html", title="Reset Password", form=form)


@users.route("/verify_email/<token>", methods=["GET", "POST"])
def verify_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_token(token)
    if user is None:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))

    user.email_verified = True
    db.session.commit()
    flash(
        f"{user.first_name} your account has been successfully created. you can not login!",
        "success",
    )
    return redirect(url_for("users.login"))
