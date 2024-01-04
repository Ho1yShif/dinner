import json
import random
from typing import List
from datetime import date
import pandas as pd

class plan_dinners:
	"""
	Plan 3 weekly dinners
	Display plan and shopping list in a user-friendly format using prints
	Then build a UI for the menu planning and shopping list
	"""

	def __init__(self):
		self.today = str(date.today()).replace("-", "_")

		"""Read dinners from JSON"""
		self.dinners = json.load(open("dinners.json", "r"))
		self.dinners = dict(self.dinners)

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


	def menu(self):
		meal_options = list(self.dinners.keys())
		remaining_meals = 3
		chosen_meals = []

		"""Randomly select 3 meals and display menu"""
		random_meals = random.choices(sequence=meal_options, k=remaining_meals)
		chosen_meals.extend(random_meals)
		random.shuffle(chosen_meals)

		print(f"Length of chosen meals: {len(chosen_meals)}")

		meal_schedule = {
			"Monday": chosen_meals[0],
			"Tuesday": chosen_meals[1],
			"Wednesday": chosen_meals[2]
		}

		print(f"Menu for the week of {self.today}:")
		df = pd.DataFrame(columns=["Day", "Meal", "Ingredients", "Prep"])
		for day, meal in meal_schedule.items():
			ingredients = self.dinners[meal]["ingredients"]
			prep = self.dinners[meal]["prep"]
			df = df.append({"Day": day, "Meal": meal, "Ingredients": ingredients, "Prep": prep}, ignore_index=True)

		print(df)


