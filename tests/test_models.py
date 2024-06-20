import unittest
from flaskblog import create_app, db, bcrypt
from flaskblog.models import User
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestBase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SERVER_NAME"] = "localhost"
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            hashed_password = bcrypt.generate_password_hash("password")
            user = User(
                username="testuser",
                email="test@example.com",
                password=hashed_password,
                email_verified=True,
                first_name="Test_first_name",
                last_name="Test_last_name",
                role="Follower",
            )
            db.session.add(user)
            db.session.commit()
            self.user = User.query.first()

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class TestUserModel(TestBase):

    def test_get_reset_token(self):
        with self.app.app_context():
            token = self.user.get_reset_token()
            self.assertIsInstance(token, str)

    def test_verify_token(self):
        with self.app.app_context():
            token = self.user.get_reset_token()
            verified_user = User.verify_token(token)
            self.assertIsNotNone(verified_user)
            self.assertEqual(verified_user.id, self.user.id)

    @freeze_time("2024-06-21 12:00:00")
    def test_verify_token_expired(self):
        with self.app.app_context():
            token = self.user.get_reset_token()
            with freeze_time("2024-06-21 12:30:01"):
                expired_user = User.verify_token(token)
                self.assertIsNone(expired_user)


if __name__ == "__main__":
    unittest.main()
