"""
TODO
Unique categories weekly
Display
UI
"""

import json
import random
import pandas as pd
from datetime import date

class PlanDinners:
	"""
	Plan 3 weekly dinners
	Display plan and shopping list in a user-friendly format using prints
	Then build a UI for the menu planning and shopping list
	"""

	def __init__(self):
		self.today = str(date.today()).replace("-", "_")

		"""Read dinners from JSON"""
		with open("dinners.json", "r") as file:
			dinners_list = json.load(file)
			self.dinners = {dinner['meal']: dinner for dinner in dinners_list}
			print(type(self.dinners))

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


	def schedule(self):
		meal_options = list(self.dinners.keys())
		remaining_meals = 3

		"""Randomly select 3 meals for the weekly schedule"""
		chosen_meals = random.choices(population=meal_options,
									k=remaining_meals)
		random.shuffle(chosen_meals)

		meal_schedule = dict(zip(["Monday", "Tuesday", "Wednesday"], chosen_meals))

		"""Create meals dataframe"""
		meals_list = [
						{"Day": day,
						"Meal": meal.title(),
						"Ingredients": ', '.join(self.dinners[meal]["ingredients"]),
						"Prep": ', '.join(self.dinners[meal]["prep"])}
						for day, meal in meal_schedule.items()
					]
		meals_df = pd.DataFrame(meals_list)

		"""Display meal schedule"""
		print(f"Menu for the week of {self.today}")
		for day, meal in meal_schedule.items():
			print(f"{day}: {meal.title()}")

		return meals_df

if __name__ == "__main__":
	dinners = PlanDinners()
	schedule = dinners.menu()

