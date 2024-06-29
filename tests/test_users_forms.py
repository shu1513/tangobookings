import unittest
from flaskblog import create_app, db, bcrypt
from flaskblog.models import User
from flask_login import login_user
import logging
from flaskblog.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestBase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SERVER_NAME"] = "localhost.localdomain"
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
            logger.info("Setup complete: user created with email 'test@example.com'")

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            logger.info("Teardown complete: database cleaned")


class TestForms(TestBase):

    def test_registration_form_valid_data(self):
        with self.app.app_context():
            form = RegistrationForm(
                username="testuser2",
                email="test2@example.com",
                password="Test1234!",
                confirm_password="Test1234!",
                first_name="Test",
                last_name="User",
                role="Follower",
            )
            print(form.errors)
            self.assertTrue(form.validate(), msg=form.errors)

    def test_registration_form_invalid_email(self):
        with self.app.app_context():
            form = RegistrationForm(
                username="testuser",
                email="invalid-email",
                password="Test1234!",
                confirm_password="Test1234!",
                first_name="Test",
                last_name="User",
                role="Follower",
            )
            self.assertFalse(form.validate())
            self.assertIn("Invalid email address.", form.email.errors)

    def test_registration_form_mismatched_passwords(self):
        with self.app.app_context():
            form = RegistrationForm(
                username="testuser",
                email="test@example.com",
                password="Test1234!",
                confirm_password="Test5678!",
                first_name="Test",
                last_name="User",
                role="Follower",
            )
            self.assertFalse(form.validate())
            self.assertIn(
                "Field must be equal to password.", form.confirm_password.errors
            )

    def test_registration_form_weak_password(self):
        with self.app.app_context():
            form = RegistrationForm(
                username="testuser",
                email="test@example.com",
                password="weak",
                confirm_password="weak",
                first_name="Test",
                last_name="User",
                role="Follower",
            )
            self.assertFalse(form.validate())
            self.assertIn(
                "Password must be 8-16 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.",
                form.password.errors,
            )

    def test_login_form_valid_data(self):
        with self.app.app_context():
            form = LoginForm(email="test@example.com", password="Test1234!")
            self.assertTrue(form.validate())

    def test_login_form_missing_password(self):
        with self.app.app_context():
            form = LoginForm(email="test@example.com", password="")
            self.assertFalse(form.validate())
            self.assertIn("This field is required.", form.password.errors)

    def test_update_account_form_valid_data(self):
        with self.app.test_request_context():
            user = User.query.filter_by(email="test@example.com").first()
            login_user(user)

            form = UpdateAccountForm(
                username="newuser",
                email="new@example.com",
                first_name="New",
                last_name="User",
                role="Leader",
            )
            self.assertTrue(form.validate())

    def test_update_account_form_invalid_username(self):
        with self.app.test_request_context():

            user = User.query.filter_by(email="test@example.com").first()
            login_user(user)

            form = UpdateAccountForm(
                username="",
                email="new@example.com",
                first_name="New",
                last_name="User",
                role="Leader",
            )
            self.assertFalse(form.validate())
            self.assertIn("This field is required.", form.username.errors)

    def test_request_reset_form_valid_email(self):
        with self.app.app_context():
            form = RequestResetForm(email="test@example.com")
            self.assertTrue(form.validate())

    def test_request_reset_form_invalid_email(self):
        with self.app.app_context():
            form = RequestResetForm(email="invalid-email")
            self.assertFalse(form.validate())
            self.assertIn("Invalid email address.", form.email.errors)

    def test_reset_password_form_valid_data(self):
        with self.app.app_context():
            form = ResetPasswordForm(password="Test1234!", confirm_password="Test1234!")
            self.assertTrue(form.validate())

    def test_reset_password_form_mismatched_passwords(self):
        with self.app.app_context():
            form = ResetPasswordForm(password="Test1234!", confirm_password="Test5678!")
            self.assertFalse(form.validate())
            self.assertIn(
                "Field must be equal to password.", form.confirm_password.errors
            )


if __name__ == "__main__":
    unittest.main()
