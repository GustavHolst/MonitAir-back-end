# baked dependencies
import unittest
# installed dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# our own imports
from api import app
# example import
from example import sumFn

# python3 -m unittest discover -v
# discovers tests in CWD


class MyTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_home(self):
        result = self.app.get('/users')

# class TestSum(unittest.TestCase):
#     def test_sumFn(self):
#         """
#         Test it can add two numbers
#         """
#         x = 4
#         y = 5
#         result = sumFn(x, y)
#         self.assertEqual(result, 9)


# if __name__ == "__main__":
#     unittest.main()
