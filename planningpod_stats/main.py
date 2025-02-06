import click
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("PLANNINGPOD_SPREADSHEET_ID")
RANGE_NAME = "idle leads!A:B"  # Adjust based on where you want to write data


def fetch_number_from_webpage():
    # Create a session to maintain cookies between requests
    session = requests.Session()

    # First request to get cookies
    session.get(os.getenv("PLANNINGPOD_REPORT_URL"))
    url2 = "https://app2.planningpod.com/index.cfm?fuseaction=reports.getReportData"
    data = {
        "id": os.getenv("PLANNINGPOD_ID"),
        "start_row": "1",
        "get_report_detail": "1",
        "report_type": "primary",
    }

    response = session.post(url2, data=data)
    json_data = response.json()

    # Extract the total_records value from the nested JSON structure
    total_records = json_data["report_data"]["recordset"]["total_records"]
    return total_records


def update_sheet(number):
    creds = service_account.Credentials.from_service_account_file(
        os.getenv("SERVICE_ACCOUNT_FILE"), scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=creds)
    date = datetime.now(tz=ZoneInfo('America/Los_Angeles')).strftime('%m/%d/%Y')
    values = [[date, number]]

    body = {"values": values}

    # Append the data to the sheet
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()


@click.command()
def main():
    """Fetch the number of idle leads and update the Google Sheet."""
    number = fetch_number_from_webpage()
    click.echo(f"Found {number} idle leads")
    update_sheet(number)


if __name__ == "__main__":
    main()
