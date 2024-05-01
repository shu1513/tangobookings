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
GENDERS = ['female','male']


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
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure username exists and password is correct
        elif len(rows) != 1 or not check_password_hash(
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
        confirm_password = request.form.get("confirmPassword")
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
        if not username:
            return apology("must provide username", 403)
        elif len(username)<8 or len(username)>16 or not any(char.isdigit() or char.isalpha() for char in username):
            return apology("username must be 8 to 16 characters long, and contains at least 1 number and 1 letter.")
        elif not password:
            return apology("must provide password", 403)
        elif not confirm_password:
            return apology("must re-enter password", 403)
        elif existing_user:
            return apology(
                "this username already exist, please choose another", 403
            )
        elif password != confirm_password:
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
        elif not first_name:
            return apology("must provide first name", 403)
        elif not last_name:
            return apology("must provide lastname", 403)
        elif any(char.isdigit() or char in string.punctuation or char.isspace() for char in first_name):
            return apology("first name should not contain numbers, spaces, or special characters", 403)
        elif any(char.isdigit() or char in string.punctuation or char.isspace() for char in last_name):
            return apology("last name should not contain numbers, spaces, or special characters", 403)
        elif len(first_name) > 25:
            return apology ("first name field only allows up to 25 characters", 403)
        elif len(last_name) > 50:
            return apology ("last name field only allows up to 50 characters", 403)
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
    
    #show profile 
@app.route("/profile")
def profile():
    username = request.args.get("username")
    user_info = db.execute("SELECT * FROM users WHERE username = ?", username)[0]
    first_name, last_name = user_info["first_name"],user_info["last_name"]
    return render_template("profile.html", first_name=first_name, last_name=last_name)

@app.route("/myprofile")
@login_required
def myprofile():
    if request.method == "GET":
        user_id = session["user_id"]
        user_info = db.execute("SELECT * FROM users WHERE user_id = ?", user_id)[0]
        user_data = {'First_Name':user_info["first_name"], 'Last_Name':user_info["last_name"], 'Role':user_info["role"], 'Gender':user_info["gender"], 'Height in cm':user_info["height_cm"], 'Email':user_info["email"]}
        return render_template ("myprofile.html", user_data=user_data,ROLES=ROLES, GENDERS=GENDERS)
        #return render_template("myprofile.html", user_info=user_info, first_name=first_name, last_name=last_name, role=role, gender=gender, height_cm=height_cm, email=email, ROLES=ROLES, GENDERS=GENDERS)


@app.route("/display")
def display():
    #for loop
    username = db.execute("SELECT username FROM users WHERE")
    return redirect(f"/profile?user_id={username}")