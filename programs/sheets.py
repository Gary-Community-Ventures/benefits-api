from decouple import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import json


def sheets_get_data(spreadsheet_id, range_name):
    info = json.loads(config('SHEETS'))
    creds = service_account.Credentials.from_service_account_info(info)

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range_name).execute()
        values = result.get('values', [])
    except HttpError as err:
        values = False

    return values
