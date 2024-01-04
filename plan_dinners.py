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
			self.dinners = json.load(file)

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

		meal_schedule = {
			"Monday": chosen_meals[0],
			"Tuesday": chosen_meals[1],
			"Wednesday": chosen_meals[2]
		}

		print(f"Menu for the week of {self.today}:")
		meals_list = [
						{"Day": day, "Meal": meal,
	   					"Ingredients": self.dinners[meal]["ingredients"],
						"Prep": self.dinners[meal]["prep"]}
						for day, meal in meal_schedule.items()
					]
		meals_df = pd.DataFrame(meals_list)
		# meals_df = pd.DataFrame(columns=["Day", "Meal", "Ingredients", "Prep"])
		# for day, meal in meal_schedule.items():
		# 	ingredients = self.dinners[meal]["ingredients"]
		# 	prep = self.dinners[meal]["prep"]
		# 	meals_df = meals_df.append(
		# 				{"Day": day, "Meal": meal,
		# 				"Ingredients": ingredients,
		# 				"Prep": prep},
		# 				ignore_index=True
		# 			``	)
		return meals_df

if __name__ == "__main__":
	dinners = PlanDinners()
	dinners.menu()

