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


def show_main_menu(chat_id, shops):
    reply_keyboard = {
        'keyboard': [
            [{'text': 'Категории'}, {'text': 'Магазины'}],
        ],
        'resize_keyboard': True
    }

    send_message(chat_id, 'Выберите действия из меню ниже', reply_markup=reply_keyboard)

    keyboard = {'inline_keyboard': []}

    keyboard['inline_keyboard'].append([
        {'text': 'Магазины', 'callback_data': 'show_shops'}
    ])

    categories = shops.keys()

    for category in categories:
        button = {'text': category, 'callback_data': f'category_{category}'}
        keyboard['inline_keyboard'].append([button])

    keyboard['inline_keyboard'].append([
        {'text': 'Таблица со всеми промокодами', 'url': SHEET_URL}
    ])

    send_message(chat_id, 'Выберите категорию, в которой хотите получить скидку', keyboard)


def get_shop_keyboard(shops):
    keyboard = {'inline_keyboard': []}

    unique_shops = sorted(set(shop for shop_list in shops.values() for shop in shop_list))

    row = []
    for i, shop in enumerate(unique_shops, 1):
        button = {'text': shop, 'callback_data': f'shop_{shop}'}
        row.append(button)

        if i % 3 == 0:
            keyboard['inline_keyboard'].append(row)
            row = []

    if row:
        keyboard['inline_keyboard'].append(row)

    keyboard['inline_keyboard'].append([{'text': 'В меню', 'callback_data': 'home'}])

    return keyboard


def handle_update(update):
    shops = get_info_from_sheet()

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            send_message(chat_id, 'Добро пожаловать')
            show_main_menu(chat_id, shops)

        elif text == 'Категории':
            show_main_menu(chat_id, shops)

        elif text == 'Магазины':
            keyboard = get_shop_keyboard(shops)

            send_message(chat_id, 'Выберите: ', reply_markup=keyboard)


# for starting bot
def start() -> None:
    '''
    :return: None (return nothing)

    For starting bot.
    '''

    # for receiving new message
    offset: int | None = None

    # all users states
    user_states: dict[int, dict] = {}

    while True:
        # get new update
        updates = get_updates(offset)

        # if there is some update
        if 'result' in updates:
            for update in updates['result']:
                # save offset
                offset = update['update_id'] + 1

                # get user state
                chat_id = (
                        update.get('message', {})
                        .get('chat', {})
                        .get('id') or
                        update.get('callback_query', {})
                        .get('message', {})
                        .get('chat', {})
                        .get('id')
                )

                try:
                    # for message analys
                    handle_update(update)
                except Exception as e:
                    # in case of error
                    send_message(chat_id, f'Произошла ошибка: {e}')

            time.sleep(1)


# start bot
start()
