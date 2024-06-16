import unittest
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

    def test_logout(self):
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 200)

    def test_account(self):
        response = self.client.get("/account")
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        response = self.client.get("/reset_password")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
