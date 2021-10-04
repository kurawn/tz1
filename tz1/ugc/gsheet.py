from oauth2client.service_account import ServiceAccountCredentials
import gspread
from pathlib import Path
from django.conf import settings


def get_worksheets():
    scope = ['https://spreadsheets.google.com/feeds']
    creds_path = settings.BASE_DIR.parent / 'google.json'
    gcreds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(gcreds)
    sh = client.open_by_key('1xh9cSmp2FJbBpDxvC53tA2IL7HsUozaD59qWjbm5JBk')
    return sh
