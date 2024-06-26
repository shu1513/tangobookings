from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flaskblog import db, login_manager
from flask import current_app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.LargeBinary, nullable=False)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.png")
    posts = db.relationship("Post", backref="author", lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_reset_token(self):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        # returns a token
        token = serializer.dumps(
            {"user_id": self.id}, salt=current_app.config["PASSWORD_SALT"]
        )
        return token

    @staticmethod
    def verify_token(token):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serializer.loads(
                token, salt=current_app.config["PASSWORD_SALT"], max_age=1800
            )["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
