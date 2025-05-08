import requests
import time
import json
import gspread

BOT_TOKEN = '**'
URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
GOOGLE_JSON = r'**.json'
SHEET_URL = '**'


# getting info from sheet
def get_info_from_sheet() -> dict:
    '''
    :return: Dictionary (list of shops by category)

    Getting information from google sheet
    and adding it to dictionary for convenience of work.
    '''

    gc = gspread.service_account(filename=GOOGLE_JSON)
    sh = gc.open_by_url(SHEET_URL)
    wrksht = sh.get_worksheet(0)
    sheet_data = wrksht.get_all_values()

    shops = {}
    for row in sheet_data[1:]:
        category = row[8]
        shop = row[0]

        if category not in shops:
            shops[category] = [shop]
        else:
            shops[category].append(shop)

    return shops
