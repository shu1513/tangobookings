import os
import string

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd


# Configure application
app = Flask(__name__)


# Set HSTS header after each request
@app.after_request
def add_hsts_header(response):
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains; preload"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tangobookings1.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

ROLES = ['follower', 'leader', 'both']

@app.route("/")
def index():
    emails = db.execute("SELECT email FROM users")
    return render_template("test1.html", emails=emails)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password_hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        flash("logged in!")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("logged out!")
    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        email = request.form.get("email").strip()
        role = request.form.get("role")
        first_name = request.form.get("first_name").strip()
        last_name = request.form.get("last_name").strip()
        existing_user = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        existing_email = db.execute(
            "SELECT * FROM users WHERE email = ?", request.form.get("email")
        )
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)
        elif not request.form.get("confirmPassword"):
            return apology("must re-enter password", 403)
        elif existing_user:
            return apology(
                "this username already exist, please choose another", 403
            )
        elif request.form.get("confirmPassword") != request.form.get("password"):
            return apology("passwords words must match", 403)
        elif (
            len(password) < 8
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char.isdigit() for char in password)
            or not any(char in string.punctuation for char in password)
            ):
            return apology(
                "Passwords must be 8 to 16 digits long, containing at least 1 upper case letter and 1 lower case letter, one numeric digit, and one special character (example: @$!%*?&)",
                403,
            )
        elif existing_email:
            return apology ("the email you have entered is already associted with an account")
        elif role not in ROLES:
            return apology(
                "Please select valid role", 403
            )

        else:
            db.execute(
                "INSERT INTO users (username, password_hash, email, first_name, last_name, role) VALUES (?, ?, ?, ?, ?, ?)",
                username,
                generate_password_hash(password),
                email,
                first_name,
                last_name,
                role
            )
            user = db.execute("SELECT user_id FROM users WHERE username = ?", username)
            session["user_id"] = user[0]["user_id"]
            flash("Registered!")
            return redirect("/")
    else:
        return render_template("register.html", roles=ROLES)