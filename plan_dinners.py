"""
TODO
Possibly upload Excel output to shared Google Sheets
UI
"""

import json
import random
import pandas as pd
from datetime import date

class PlanDinners:
	"""
	Plan 3 weekly dinners along with a shopping list
	Export to Excel for easy viewing
	"""

	def __init__(self):
		self.today = str(date.today()).replace("-", "_")

		"""Read dinners from JSON"""
		with open("dinners.json", "r") as file:
			dinners_list = json.load(file)
			self.dinners = {dinner["meal"]: dinner for dinner in dinners_list}

		"""Set static list attributes"""
		self.staples = ["garlic", "olive oil", "neutral oil",
				"salt", "pepper", "vegan butter",
				"eggs", "mayonnaise", "vegetable broth",
				"vegan parmesan", "vegan cheese", "chia seeds"]
		self.staples.sort()

		self.fresh_veg = ["spinach", "carrots", "asparagus",
					"orange/yellow peppers", "cabbage",
					"zucchini", "squash", "cucumber",
					"snap peas", "brussels sprouts"]

		self.frozen_veg = ["broccoli", "cauliflower", "peas", "green beans"]

		self.toppings = ["hemp seeds", "pumpkin seeds", "avocado", "cottage cheese"]

	def schedule_meals(self):
		"""Build meal schedule for the week along with ingredients and ahead-of-time prep instructions"""

		meal_options = list(self.dinners.keys())
		chosen_meals, meal_categories = [], []

		"""Randomly select 3 meals for the weekly schedule"""
		while len(chosen_meals) < 3:
			chosen_meal = random.choice(meal_options)
			category = self.dinners[chosen_meal]["category"]
			"""Allow for only one meal per category per week"""
			if category not in meal_categories:
				meal_categories.append(category)
				meal_options.remove(chosen_meal)
				chosen_meals.append(chosen_meal)
			else:
				continue

		"""Create meal schedule and dataframe"""
		self.meal_schedule = dict(zip(["Monday", "Tuesday", "Wednesday"], chosen_meals))
		meals_list = [
					{"Day": day,
					"Meal": meal.title(),
					"Ingredients": ", ".join(self.dinners[meal]["ingredients"]),
					"Prep": ", ".join(self.dinners[meal]["prep"])}
					for day, meal in self.meal_schedule.items()
					]
		self.meals_df = pd.DataFrame(meals_list)

		"""Display meal schedule"""
		print(f"Menu for the week of {self.today}")
		for day, meal in self.meal_schedule.items():
			print(f"{day}: {meal.title()}")

		return self.meals_df

	def shopping(self):
		"""Build shopping list for the week based on staples, vegetables, toppings, and the meal plan"""

		"""Create list from randomly chosen vegetable and topping items"""
		fresh_veg_items = random.sample(self.fresh_veg, 2)
		frozen_veg_item = random.sample(self.frozen_veg, 1)
		topping_items = random.sample(self.toppings, 2)
		veggies_toppings = fresh_veg_items + frozen_veg_item + topping_items
		veggies_toppings.sort()

		"""Create shopping list for meal ingredients"""
		shopping_list = list({item for meal in self.meal_schedule.values() for item in self.dinners[meal]["ingredients"]})
		shopping_list.sort()

		"""Pad lists to make them all the same length for a uniform dataframe"""
		lists = [self.staples, shopping_list, veggies_toppings]
		max_len = max(len(lst) for lst in lists)
		for idx, lst in enumerate(lists):
			lists[idx] += [''] * (max_len - len(lst))

		"""Create dataframe where each ingredient has its own line"""
		self.shopping_df = pd.DataFrame(
						{"Check Staples": self.staples,
							"Veggies and Toppings": veggies_toppings,
							"Meal Ingredients": shopping_list}
						)

		return self.shopping_df

	def export(self):
		"""Schedule meals, create shopping list, and export them to an Excel workbook with two separate sheets"""

		PlanDinners.schedule_meals(self)
		PlanDinners.shopping(self)

		excel_path = f"~/Desktop/dinners_{self.today}.xlsx"
		with pd.ExcelWriter(excel_path) as writer:
			self.meals_df.to_excel(writer, sheet_name="Meals", index=False)
			self.shopping_df.to_excel(writer, sheet_name="Shopping", index=False)

		print(f"Exported meal plan to {excel_path}")

if __name__ == "__main__":
	dinners = PlanDinners()
	dinners.export()
