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
    reply_keyboard = {
        'keyboard': [
            [{'text': 'Категории'}, {'text': 'Магазины'}],
        ],
        'resize_keyboard': True
    }

    send_message(chat_id, 'Выберите действие из меню ниже:', reply_markup=reply_keyboard)

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

def get_shop_keyboard():
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

    return keyboard


def handle_update(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            send_message(chat_id, 'Добро пожаловать!')

            show_main_menu(chat_id)

        elif text == 'Категории':
            show_main_menu(chat_id)

        elif text == 'Магазины':
            keyboard = get_shop_keyboard()

            send_message(chat_id, 'Выберите: ', reply_markup=keyboard)

    elif 'callback_query' in update:
        callback = update['callback_query']
        data = callback['data']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']

        edit_message(chat_id, message_id, text='Рады вас видеть!')

        if data == 'home':
            show_main_menu(chat_id)

        elif data == 'show_shops':
            keyboard = get_shop_keyboard()
            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        elif data.startswith('category_'):
            selected_category = data.replace('category_', '')

            filtered_row = [row for row in sheet_data if len(row) > 8 and row[8] == selected_category]
            shops = list(set([row[0] for row in filtered_row]))

            keyboard = {'inline_keyboard': []}
            for shop in shops:
                button = {'text': shop, 'callback_data': f'shop_{shop}'}
                keyboard['inline_keyboard'].append([button])

            home = {'text': 'В меню', 'callback_data': 'home'}
            keyboard['inline_keyboard'].append([home])

            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        elif data.startswith('shop_'):
            selected_shop = data.replace('shop_', '')

            filtered_rows = [row for row in sheet_data if row[0] == selected_shop]
            proms = [row[3] for row in filtered_rows]

            keyboard = {'inline_keyboard': []}
            for prom in proms:
                button = {'text': prom, 'callback_data': f'prom_{prom}'}
                keyboard['inline_keyboard'].append([button])

            home = {'text': 'В меню', 'callback_data': 'home'}
            keyboard['inline_keyboard'].append([home])

            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        elif data.startswith('prom_'):
            selected_prom = data.replace('prom_', '')

            for row in sheet_data:
                if row[3] == selected_prom:
                    discount = row
                    break

            send_message(chat_id, 'Чтобы воспользоваться акцией необходимо: перейти по ссылке '
                                  'или скопировать промокод и ввести его на сайте или '
                                  'приложении магазина')

            text = (f'Название: {discount[0]}\n'
                    f'Скидка: {discount[3]}\n'
                    f'Ссылка: {discount[4]}\n'
                    f'Действует до: {discount[5]}\n'
                    f'Регион: {discount[6]}\n'
                    f'Условия акции: {discount[7]}')

            send_message(chat_id, text)

            keyboard = {'inline_keyboard': []}

            home = {'text': 'В меню', 'callback_data': 'home'}
            keyboard['inline_keyboard'].append([home])

            tg_channel = {'text': 'Подпишитесь на канал', 'url': 'https://t.me/skidkinezagorami'}
            keyboard['inline_keyboard'].append([tg_channel])

            send_message(chat_id, 'Куда отправимся за скидками дальше?', reply_markup=keyboard)


while True:
    updates = get_updates(offset)
    if 'result' in updates:
        for update in updates['result']:
            offset = update['update_id'] + 1
            handle_update(update)
    time.sleep(1)
