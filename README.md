# Dinner Repo

Meal plan automation repository to streamline weekly meal planning and shopping

**Screenshots**
![image](https://github.com/Ho1yShif/dinner/assets/40185666/b2e40616-6ea0-4930-943e-a3a46d165ba1)
![Staples](https://github.com/Ho1yShif/dinner/assets/40185666/bc608e33-3374-4526-971f-9aa0c0361621)

## How to use

1. Create a Google Sheet with two sheets, `Meals` and `Shopping`

   ![image](https://github.com/Ho1yShif/dinner/assets/40185666/2c688c51-7fac-4ad9-b3f6-7f885b261be1)

2. Set up a Google Cloud service account with access to the Google Sheets API and create a new JSON key ([Learn more about Service Accounts.](https://cloud.google.com/iam/docs/service-account-overview?authuser=4))

   - Replace the `\n` in the key with `\\n` so Python's json library can parse it
   - Encode the santized key JSON in base64 so it can be easily stored in GitHub Secrets

3. Fork this repo

   - Customize your meal plan using the `dinners.json` file

4. Set repo actions Secrets
   - `SERVICE_ACCOUNT` is the Google service account JSON file encoded in base64
   - `SPREADSHEET_ID` is the ID of your Google Sheet (the long string in the URL)

## How it works

A GitHub Action is scheduled to run the `plan_dinners.py` script weekly at 3 AM on Saturday. This script will read the `dinners.json` file and randomly select meals for each day of the week. Each meal category will be represented only once per week to avoid repetition.

After making selections, the script then updates the `Meals` sheet with the chosen meals and updates the `Shopping` sheet with the ingredients needed for those meals. The shopping list will also include a reminder to check if you are stocked on staples like eggs, bread, oil, etc.
