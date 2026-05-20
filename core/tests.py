from django.test import TestCase
from .utils import calculate_water_goal, calculate_daily_status


class WaterSystemTest(TestCase):

    def test_water_goal(self):
        result = calculate_water_goal(
            age=25,
            weight=70,
            gender="Male",
            activity="Moderate",
            weather="Hot"
        )
        self.assertEqual(result, 3300)

    def test_daily_status(self):
        result = calculate_daily_status(3300, 1800)

        self.assertEqual(result["remaining_ml"], 1500)