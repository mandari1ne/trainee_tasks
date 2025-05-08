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

    try:
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
    except Exception as e:
        print(f'{e}: Не удается получить данные из таблицы')
        return {}

# for checking user messages
def get_updates(offset: int = None) -> dict:
    '''
    :param offset: Integer (id of last processed message to receive new ones)
    :return: Dictionary (list of updates)

    Get new updates from Telegram server via the getUpdates.
    '''

    try:
        # request params
        params = {'timeout': 100, 'offset': offset}
        resp = requests.get(URL + '/getUpdates', params=params)

        # check request status
        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException as e:
        # in case of error
        return {'result': []}


# for sending message to user
def send_message(chat_id: int, text: str, reply_markup: dict = None) -> dict | None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param text: String (message text for sending)
    :param reply_markup: Dictionary (keyboard for user)
    :return: Dictionary | None (response from Telegram server, or None in case of error)

    Send text message to user.
    '''

    try:
        # request params
        params = {'chat_id': chat_id, 'text': text}
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)

        resp = requests.get(URL + '/sendMessage', params=params)

        # check request status
        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException as e:
        # in case of error
        return None


# for edit message
def edit_message(chat_id: int, message_id: int, text: str = None, reply_markup: dict = None) -> dict | None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param message_id: Integer (id of message)
    :param text: String (text of message)
    :param reply_markup: Dictionary (keyboard for user)
    :return: Dictionary | None (response from Telegram server, or None in case of error)

    Edit and send message.
    '''

    try:
        # request params
        params = {'chat_id': chat_id, 'message_id': message_id}

        # if message exists
        if text:
            params['text'] = text

            # request method
            method = '/editMessageText'
        else:
            # request method
            method = '/editMessageReplyMarkup'

        # if reply markup exists
        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)

        # send request
        resp = requests.get(URL + method, params=params)

        # check request state
        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException:
        # in case of error
        return None
