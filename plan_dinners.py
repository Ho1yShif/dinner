import json
from typing import List
from datetime import date


class plan_dinners:
	"""
	Plan 3 weekly dinners
	Display plan and shopping list in a user-friendly format using prints
	Then build a UI for the menu planning and shopping list
	"""
	def __init__(self, meals:List[str]):
		self.meals = meals
		self.today = str(date.today()).replace("-", "_")

		"""Set staple lists"""
		self.staples = ["garlic", "olive oil", "neutral oil",
				"salt", "pepper", "vegan butter",
				"eggs", "mayonnaise", "vegetable broth",
				"vegan parmesan", "vegan cheese"]

		self.fresh_veg = ["spinach", "carrots", "asparagus",
					"orange peppers", "yellow peppers", "cabbage",
					"zucchini", "squash", "cucumber",
					"snap peas", "brussels sprouts"]

		self.frozen_veg = ["broccoli", "cauliflower", "peas", "green beans"]

		self.toppings = ["hemp seeds", "pumpkin seeds", "avocado", "cottage cheese"]

