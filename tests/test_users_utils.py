import unittest
from unittest.mock import patch, MagicMock
from flaskblog import create_app, db, bcrypt
from flaskblog.models import User
from flaskblog.users.utils import save_picture, remove_old_picture, send_reset_email
from PIL import Image
from flask import url_for


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

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class TestUtils(TestBase):

    def test_save_picture(self):
        with self.app.app_context(), patch(
            "flaskblog.users.utils.secrets.token_hex"
        ) as mock_token_hex, patch(
            "flaskblog.users.utils.os.path.splitext"
        ) as mock_splitext, patch(
            "flaskblog.users.utils.Image.open"
        ) as mock_image_open, patch(
            "flaskblog.users.utils.current_app"
        ) as mock_current_app:

            mock_current_app.root_path = "/fakepath"
            mock_token_hex.return_value = "randomhex"
            mock_splitext.return_value = ("filename", ".jpg")

            mock_form_picture = MagicMock()
            mock_form_picture.filename = "test.jpg"
            mock_image = MagicMock(spec=Image.Image)
            mock_image_open.return_value = mock_image

            file_name = save_picture(mock_form_picture)

            mock_token_hex.assert_called_once()
            mock_splitext.assert_called_once_with("test.jpg")
            mock_image_open.assert_called_once_with(mock_form_picture)
            mock_image.thumbnail.assert_called_with((125, 125))
            mock_image.save.assert_called_with(
                "/fakepath/static/profile_pics/randomhex.jpg"
            )

            self.assertEqual(file_name, "randomhex.jpg")

    def test_remove_old_picture(self):
        with self.app.app_context(), patch(
            "flaskblog.users.utils.current_app"
        ) as mock_current_app, patch("flaskblog.users.utils.os.remove") as mock_remove:

            mock_current_app.root_path = "/fakepath"
            remove_old_picture("test.jpg")
            mock_remove.assert_called_once_with(
                "/fakepath/static/profile_pics/test.jpg"
            )
            # Test case where old_pic is default.png
            mock_remove.reset_mock()
            remove_old_picture("default.png")
            mock_remove.assert_not_called()

    def test_send_reset_email(self):
        with self.app.app_context(), patch(
            "flaskblog.users.utils.Message"
        ) as mock_Message, patch("flaskblog.users.utils.mail.send") as mock_mail_send:

            user = User.query.filter_by(email="test@example.com").first()

            user.get_reset_token = MagicMock(return_value="dummytoken")
            send_reset_email(user)

            mock_Message.assert_called_with(
                "Password Reset Request",
                sender="shu151343@gmail.com",
                recipients=["test@example.com"],
            )
            mock_mail_send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
