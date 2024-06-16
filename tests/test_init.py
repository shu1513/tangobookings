import unittest
from flaskblog import create_app


class InitTest(unittest.TestCase):
    def test_create_app(self):
        app = create_app()
        self.assertIsNotNone


if __name__ == "__main__":
    unittest.main()
