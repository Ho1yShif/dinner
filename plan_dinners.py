import os
import json
import random
import base64
import datetime
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


class PlanDinners:
    """Plan weekly dinners along with a shopping list; export to Google Sheets for easy viewing"""

    def read_dinners_json(self):
        """Read data from dinners.json"""
        with open("dinners.json", "r") as file:
            dinners_dict = json.load(file)
            self.meals = {meal["name"]: meal for meal in dinners_dict["meals"]}
            self.staples = dinners_dict["shared_ingredients"]["staples"]
            self.fresh_veg = dinners_dict["shared_ingredients"]["fresh_vegetables"]
            self.frozen_veg = dinners_dict["shared_ingredients"]["frozen_vegetables"]
            self.toppings = dinners_dict["shared_ingredients"]["toppings"]

    def read_config_json(self):
        """Read data from config.json"""
        with open("config.json", "r") as file:
            config_dict = json.load(file)
            self.chefs = config_dict["chefs"]
            self.chef_responsibilities = config_dict["chef_responsibilities"]

    def setup_google_sheets_auth(self):
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

    def __init__(self):
        today = datetime.date.today()
        self.start_of_week = today + datetime.timedelta(days=6-today.weekday())
        self.week_timestamp = self.start_of_week.strftime('%b %d, %Y')

        PlanDinners.setup_google_sheets_auth(self)
        PlanDinners.read_dinners_json(self)
        PlanDinners.read_config_json(self)

    def __str__(self) -> str:
        """Return a string representation of the weekly meal plan"""
        if self.meal_schedule:
            str_info = f"PlanDinners({self.week_timestamp})\n" + \
                "\n".join([f"{day}: {meal.title()}" for day,
                          meal in self.meal_schedule.items()])
        else:
            str_info = f"PlanDinners({self.week_timestamp})\nMeals have not been scheduled yet"
        return str_info

    def __repr__(self) -> str:
        """Return a string representation of the PlanDinners object"""
        if self.meal_schedule:
            repr_info = f"PlanDinners(meal_schedule={self.meal_schedule})"
        else:
            repr_info = f"PlanDinners({self.week_timestamp})\nMeals have not been scheduled yet"
        return repr_info

    def schedule_meals(self):
        """Build meal schedule for the week along with ingredients and ahead-of-time prep instructions"""
        chef_meals = {chef: [] for chef in self.chefs}
        for meal_name in list(self.meals.keys()):
            meal = self.meals[meal_name]
            for idx, chef in enumerate(meal["chef_capabilities"]):
                chef_meals[chef].append(meal_name)

        chosen_meal_names = []
        last_categories = []

        for day, chef in self.chef_responsibilities.items():
            """Skip if no chef is assigned to a given day"""
            if chef == "":
                chosen_meal_names.append("")
                continue

            """Randomly select a meal from the chef's list of capabilities"""
            chosen_meal_name = random.choice(chef_meals[chef])
            curr_categories = self.meals[chosen_meal_name]["categories"]

            """
            Ensure that meals with shared categories are not scheduled on consecutive days
            and that no meal is scheduled more than once

            Pick a new meal if the current choice is invalid
            """
            while any(category in last_categories for category in curr_categories) or chosen_meal_name in chosen_meal_names:
                chosen_meal_name = random.choice(chef_meals[chef])
                curr_categories = self.meals[chosen_meal_name]["categories"]

            chosen_meal_names.append(chosen_meal_name)
            last_categories = curr_categories

        """Create meal schedule and dataframe"""
        self.meal_schedule = dict(
            zip(list(self.chef_responsibilities.keys()), chosen_meal_names))

        meals_dict = {}
        for day, meal_name in self.meal_schedule.items():
            if meal_name == "":
                meals_dict[day] = ["Unplanned", "Group",
                                   "Whatever is available", "N/A"]
                continue
            meals_dict[day] = [
                meal_name.title(),
                "Chef " + self.chef_responsibilities[day],
                ", ".join(self.meals[meal_name]["ingredients"]),
                ", ".join(self.meals[meal_name]["prep"])
            ]

        self.meals_df = pd.DataFrame(
            meals_dict, index=["Meal", "Chef", "Ingredients", "Prep"]
        )

        """Display meal schedule"""
        print(self.__str__())

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
        shopping_dict = {}
        for day, meal_name in self.meal_schedule.items():
            if meal_name == "":
                continue
            meal = self.meals[meal_name]
            for idx, ingredient in enumerate(meal["ingredients"]):
                if ingredient in self.staples:
                    continue
                shopping_dict[ingredient] = shopping_dict.get(
                    ingredient, 0) + 1

        """Create shopping list with 'item (COUNT meals)' format"""
        shopping_list = []
        for ingredient, count in shopping_dict.items():
            if count > 1:
                shopping_list.append(f"{ingredient} ({count} meals)")
            else:
                shopping_list.append(ingredient)
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

        """Insert row headers headers and timestamp"""
        self.meals_df.insert(0, f"Menu – Week of {self.week_timestamp}", [
                             "Meal", "Chef", "Ingredients", "Prep"], True)

        """Clear Shopping sheet before refilling with new data"""
        service = build("sheets", "v4", credentials=self.credentials)
        service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id, range="Shopping", body={}
        ).execute()

        """Update Google Sheet with latest meal plan"""
        PlanDinners.update_sheet(
            self,
            "Meals!A:H",
            "USER_ENTERED",
            # Include column headers
            [self.meals_df.columns.values.tolist()] +
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
