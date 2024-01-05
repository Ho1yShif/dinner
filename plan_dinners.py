import os
import json
import random
import base64
import pandas as pd
from datetime import date
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError


class PlanDinners:
	"""
	Plan 3 weekly dinners along with a shopping list
	Exports to Google Sheets for easy viewing
	"""

	def __init__(self):
		self.today = str(date.today())

		"""Authenticate with Google Sheets API"""
		self.spreadsheet_id = os.environ.get("SPREADSHEET_ID")
		if not self.spreadsheet_id:
			raise ValueError(
				"Please set the SPREADSHEET_ID environment variable to the ID of your Google Sheet."
			)

		service_account_info = os.environ.get("SERVICE_ACCOUNT")
		if not service_account_info:
			raise ValueError(
				"Please set the SERVICE_ACCOUNT environment variable to the contents of your service account JSON file."
			)
		self.credentials = service_account.Credentials.from_service_account_info(
			info=json.loads(
				# The JSON string is B64-encoded to avoid control chars causing issues in the pipeline
				base64.b64decode(service_account_info.encode("ascii"))
			),
			scopes=['https://www.googleapis.com/auth/spreadsheets']
		)

		"""Read data from JSON"""
		with open("dinners.json", "r") as file:
			dinners_dict = json.load(file)
			self.meals = {
				meal["name"]: meal for meal in dinners_dict["meals"]}
			self.staples = dinners_dict["shared_ingredients"]["staples"]
			self.fresh_veg = dinners_dict["shared_ingredients"]["fresh_vegetables"]
			self.frozen_veg = dinners_dict["shared_ingredients"]["frozen_vegetables"]
			self.toppings = dinners_dict["shared_ingredients"]["toppings"]

	def schedule_meals(self):
		"""Build meal schedule for the week along with ingredients and ahead-of-time prep instructions"""

		meal_options = list(self.meals.keys())
		chosen_meals, meal_categories = [], []

		"""Randomly select 3 meals for the weekly schedule"""
		while len(chosen_meals) < 3:
			chosen_meal = random.choice(meal_options)
			category = self.meals[chosen_meal]["category"]
			"""
			Allow for only one meal per category per week
			TODO: This can be done more elegantly by bucketing meals into
			categories, then picking random category buckets and removing the category once used
			"""
			if category not in meal_categories:
				meal_categories.append(category)
				meal_options.remove(chosen_meal)
				chosen_meals.append(chosen_meal)
			else:
				continue

		"""Create meal schedule and dataframe"""
		self.meal_schedule = dict(
			zip(["Monday", "Tuesday", "Wednesday"], chosen_meals))
		meals_list = [
			{"Day": day,
			 "Meal": meal.title(),
			 "Ingredients": ", ".join(self.meals[meal]["ingredients"]),
			 "Prep": ", ".join(self.meals[meal]["prep"])}
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
		shopping_list = list({item for meal in self.meal_schedule.values()
							  for item in self.meals[meal]["ingredients"]})
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

	def update_sheet(self, range_name, value_input_option, values):
		try:
			service = build("sheets", "v4", credentials=self.credentials)
			body = {"values": values}
			result = (
				service.spreadsheets()
				.values()
				.update(
					spreadsheetId=self.spreadsheet_id,
					range=range_name,
					valueInputOption=value_input_option,
					body=body,
				)
				.execute()
			)
			print(f"{result.get('updatedCells')} cells updated.")
			return result
		except HttpError as error:
			print(f"An error occurred: {error}")
			return error

	def export(self):
		"""Schedule meals, create shopping list, and update a Google Sheet with Meals and Shopping sheets"""

		"""Pick meals and create shopping list"""
		PlanDinners.schedule_meals(self)
		PlanDinners.shopping(self)

		"""Update Google Sheet with latest meal plan"""
		PlanDinners.update_sheet(
			self,
			"Meals!A:E",
			"USER_ENTERED",
			# Include column headers and timestamp
			[self.meals_df.columns.values.tolist() + [f"Menu for the week of {self.today}"]] +
			self.meals_df.values.tolist()
		)
		PlanDinners.update_sheet(
			self,
			"Shopping!A:C",
			"USER_ENTERED",
			# Include column headers
			[self.shopping_df.columns.values.tolist()] +
			self.shopping_df.values.tolist()
		)

		print(f"Successfully updated Google Sheet menu at the following link:")
		print("https://docs.google.com/spreadsheets/d/17fn-HNkRlrXHiapxXC-Uallu2zBQSiASRTRY3Hw8Ynk/edit#gid=0")



if __name__ == "__main__":
	dinners = PlanDinners()
	dinners.export()
