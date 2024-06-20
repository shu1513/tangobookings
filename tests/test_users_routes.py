"""import unittest
from flaskblog import create_app


class TestUserRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)

    def test_account(self):
        response = self.client.get("/account")
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        response = self.client.get("/reset_password")
        self.assertEqual(response.status_code, 200)
"""

import unittest
from unittest.mock import patch
from flask import url_for
from flaskblog import create_app, db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm
from flask_login import current_user


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

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class TestRegistrationRoute(TestBase):
    def test_register_post(self):
        with (
            patch(
                "flaskblog.users.routes.RegistrationForm", autospec=True
            ) as MockRegistrationForm,
            patch(
                "flaskblog.users.routes.db.session.commit", autospec=True
            ) as mock_commit,
            patch(
                "flaskblog.users.routes.send_verify_email", autospec=True
            ) as mock_send_verify_email,
        ):
            with self.client:
                form = MockRegistrationForm.return_value
                form.validate_on_submit.return_value = True
                form.username.data = "newuser"
                form.email.data = "newuser@example.com"
                form.password.data = "password"
                form.first_name.data = "testf"
                form.last_name.data = "testl"
                form.role.data = "Follower"
                with self.app.app_context():
                    response = self.client.post(url_for("users.register"))
                    self.assertEqual(response.status_code, 302)
                    mock_commit.assert_called_once()
                    mock_send_verify_email.assert_called_once()


class TestLoginRoute(TestBase):
    @patch("flaskblog.users.routes.LoginForm", autospec=True)
    @patch("flaskblog.users.routes.login_user")
    def test_login_post(self, mock_login_user, MockLoginForm):
        with self.client:
            form = MockLoginForm.return_value
            form.validate_on_submit.return_value = True
            form.email.data = "test@example.com"
            form.password.data = "password"
            form.remember.data = True

            with self.app.app_context():

                user = User.query.filter_by(email="test@example.com").first()
                self.assertIsNotNone(user, "User should exist in the test database.")

                response = self.client.post(
                    url_for("users.login"),
                    data={
                        "email": form.email.data,
                        "password": form.password.data,
                        "remember": form.remember.data,
                    },
                )
                self.assertEqual(response.status_code, 302)
                mock_login_user.assert_called_once_with(
                    user, remember=form.remember.data
                )


class TestLogoutRoute(TestBase):
    def test_logout(self):
        with self.client:
            with self.app.app_context():
                self.client.post(
                    url_for("users.login"),
                    data={"email": "test@example.com", "password": "password"},
                )
                response = self.client.get(url_for("users.logout"))
                self.assertEqual(response.status_code, 302)
                self.assertFalse(current_user.is_authenticated)


class TestAccountRoute(TestBase):
    @patch("flaskblog.users.routes.UpdateAccountForm", autospec=True)
    @patch("flaskblog.users.routes.save_picture", autospec=True)
    @patch("flaskblog.users.routes.remove_old_picture", autospec=True)
    def test_account_post(
        self, mock_remove_old_picture, mock_save_picture, MockUpdateAccountForm
    ):
        mock_save_picture.return_value = "new_pic.jpg"

        with self.client:
            with self.app.app_context():
                # Log in the user
                self.client.post(
                    url_for("users.login"),
                    data={"email": "test@example.com", "password": "password"},
                )

                # Mock the form and its return values

                form = MockUpdateAccountForm.return_value
                form.validate_on_submit.return_value = True
                form.username.data = "updateduser"
                form.email.data = "updated@example.com"
                form.first_name.data = "Updated"
                form.last_name.data = "User"
                form.role.data = "Leader"

                # Use a simple object to mock the file upload data
                class FakeFile:
                    filename = "new_pic.jpg"

                form.picture.data = FakeFile()

                # Submit the form
                response = self.client.post(url_for("users.account"))

                # Check the response
                self.assertEqual(response.status_code, 302)  # Check for redirect

                # Check that the save_picture and remove_old_picture functions were called
                mock_save_picture.assert_called_once_with(form.picture.data)
                mock_remove_old_picture.assert_called_once()

                # Verify that the user data was updated in the database
                user = User.query.filter_by(email="updated@example.com").first()
                self.assertIsNotNone(user)
                self.assertEqual(user.username, "updateduser")
                self.assertEqual(user.first_name, "Updated")
                self.assertEqual(user.last_name, "User")
                self.assertEqual(user.role, "Leader")
                self.assertEqual(user.image_file, "new_pic.jpg")


if __name__ == "__main__":
    unittest.main()
