from django.test import TestCase

from api.calc import add, subtract


class CalcTests(TestCase):

    def test_add_number(self):
        """should return the right sum"""

        self.assertEqual(add(4, 8), 12)

    def test_subtract_number(self):
        """should return the right subtraction"""

        self.assertEqual(subtract(10, 4), 6)
