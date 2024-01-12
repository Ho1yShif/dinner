"""One-time file used to add a zack_flag attribute to each meal in dinners.json"""

import json

"""Step 1: Load the data"""
with open("dinners.json", "r") as file:
    dinners_dict = json.load(file)
    meals = {meal["name"]: meal for meal in dinners_dict["meals"]}

"""Step 2: Add "zack_flag": False to each meal"""
for meal_name in meals:
    meals[meal_name]["zack_flag"] = False

"""Step 3: Write the modified data back to the file"""
with open("new_dinners.json", "w") as f:
    json.dump(meals, f, indent=4)
