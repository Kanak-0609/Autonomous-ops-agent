import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = "1bUR7ibwoM9kfLoYMJGoU3poyHiknd7_h7_R-FtXHV9Y"
CREDENTIALS_PATH = "sheets_credentials.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


def get_client_record(email: str) -> dict | None:
    """Look up a client's CRM record by email address."""
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    records = sheet.get_all_records()

    for record in records:
        if record.get("email", "").lower() == email.lower():
            return record
    return None


def update_client_status(email: str, new_status: str) -> bool:
    """Update a client's status field by email address."""
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    cell = sheet.find(email)

    if cell is None:
        return False

    headers = sheet.row_values(1)
    status_col = headers.index("status") + 1
    sheet.update_cell(cell.row, status_col, new_status)
    return True

def debug_print_all():
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    print("Headers:", sheet.row_values(1))
    print("All records:", sheet.get_all_records())

if __name__ == "__main__":
    record = get_client_record("sarah.jones@acmewidgets.com")
    print("Found record:", record)