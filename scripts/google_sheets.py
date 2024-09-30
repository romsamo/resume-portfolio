import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

def get_google_sheets_data():
    try:
        # Define the scope of access
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Use the full path to your credentials JSON file
        creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/romano/Desktop/twitterBot/config/trader_gsheets_api.json', scope)

        # Authorize the client
        client = gspread.authorize(creds)

        # Open the Google Sheet (replace with your actual Google Sheet name)
        sheet = client.open('Trade log 24-25')

        # Access the "Trades" worksheet by name
        worksheet = sheet.worksheet('Trades')
        print(f"Opened sheet: {worksheet.title}")

        # Fetch all rows from the "Trades" worksheet (including the header row)
        data = worksheet.get_all_values()  # Fetches all rows as a list of lists

        # Print the fetched data to verify
        print("Fetched data: ", data)

        # Define the path to save the CSV
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(project_root, 'data/raw_google_sheets_data.csv')

        # Save the raw data to a CSV file
        if data:
            df = pd.DataFrame(data)  # Convert list of lists to DataFrame
            df.to_csv(csv_path, index=False, header=False)  # Save without inferring headers
            print(f"Raw data retrieved and saved to CSV at {csv_path}.")
        else:
            print("No data found in the Google Sheet.")

        return data

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
get_google_sheets_data()
