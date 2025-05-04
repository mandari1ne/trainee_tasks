import requests
import time
import json
import gspread

BOT_TOKEN = '****'
URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
GOOGLE_JSON = r'***.json'
SHEET_URL = '**'

gc = gspread.service_account(filename=GOOGLE_JSON)
sh = gc.open_by_url(SHEET_URL)
wrksht = sh.get_worksheet(0)
sheet_data = wrksht.get_all_values()

offset = None


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


def send_message(chat_id, text, reply_markup=None):
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


def edit_message(chat_id, message_id, text=None, reply_markup=None):
    try:
        params = {'chat_id': chat_id, 'message_id': message_id}

        if text:
            params['text'] = text
            method = '/editMessageText'
        else:
            method = '/editMessageReplyMarkup'

        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)

        resp = requests.get(URL + method, params=params)

        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException:
        return None


def show_main_menu(chat_id):
    categories = sorted(list(set([row[8] for row in sheet_data[1:] if len(row) > 8])))

    keyboard = {'inline_keyboard': []}

    keyboard['inline_keyboard'].append([
        {'text': 'Магазины', 'callback_data': 'show_shops'}
    ])

    for category in categories:
        button = {'text': category, 'callback_data': f'category_{category}'}
        keyboard['inline_keyboard'].append([button])

    keyboard['inline_keyboard'].append([
        {'text': 'Таблица со всеми промокодами', 'url': SHEET_URL}
    ])

    send_message(chat_id, 'Выберите категорию, в которой хотите получить скидку:', keyboard)


def handle_update(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            send_message(chat_id, 'Добро пожаловать!')

            show_main_menu(chat_id)

    elif 'callback_query' in update:
        callback = update['callback_query']
        data = callback['data']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']

        edit_message(chat_id, message_id, text='Рады вас видеть!')

        if data == 'home':
            show_main_menu(chat_id)
        elif data == 'show_shops':
            keyboard = {'inline_keyboard': []}

            shops = sorted(list(set([row[0] for row in sheet_data[1:]])))
            row = []
            for i, shop in enumerate(shops, 1):
                button = {'text': shop, 'callback_data': f'shop_{shop}'}
                row.append(button)

                if i % 3 == 0:
                    keyboard['inline_keyboard'].append(row)
                    row = []

            if row:
                keyboard['inline_keyboard'].append(row)

            home = {'text': 'В меню', 'callback_data': f'home'}
            keyboard['inline_keyboard'].append([home])

            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)


while True:
    updates = get_updates(offset)
    if 'result' in updates:
        for update in updates['result']:
            offset = update['update_id'] + 1
            handle_update(update)
    time.sleep(1)
