import requests
import time
import json
import gspread

BOT_TOKEN = '***'
URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
GOOGLE_JSON = r'***.json'
SHEET_URL = '***'

gc = gspread.service_account(filename=GOOGLE_JSON)
sh = gc.open_by_url(SHEET_URL)
wrksht = sh.get_worksheet(0)
sheet_data = wrksht.get_all_values()


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


# for showing main menu
def show_main_menu(chat_id: int) -> None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :return: None (return nothing)

    This method for showing category menu.
    '''

    # initial reply keyboard
    reply_keyboard = {
        'keyboard': [
            [{'text': 'Категории'}, {'text': 'Магазины'}],
        ],
        # for better visualizing
        'resize_keyboard': True
    }

    send_message(chat_id, 'Выберите действие из меню ниже:', reply_markup=reply_keyboard)

    # getting categories of shops from google sheet
    categories = sorted(list(set([row[8] for row in sheet_data[1:] if len(row) > 8])))

    # initial keyboard
    keyboard = {'inline_keyboard': []}

    keyboard['inline_keyboard'].append([
        {'text': 'Магазины', 'callback_data': 'show_shops'}
    ])

    # add all categories in the keyboard
    for category in categories:
        button = {'text': category, 'callback_data': f'category_{category}'}
        keyboard['inline_keyboard'].append([button])

    # add url of google sheet in the keyboard
    keyboard['inline_keyboard'].append([
        {'text': 'Таблица со всеми промокодами', 'url': SHEET_URL}
    ])

    send_message(chat_id, 'Выберите категорию, в которой хотите получить скидку:', keyboard)


# getting shop menu
def get_shop_keyboard() -> dict:
    '''
    :return: Dictionary (keyboard of shops)

    This nmethod for showing shop menu.
    '''

    # initial keyboard
    keyboard = {'inline_keyboard': []}

    # getting shops from google sheet
    shops = sorted(list(set([row[0] for row in sheet_data[1:]])))

    # add shop in the keyboard
    row = []
    for i, shop in enumerate(shops, 1):
        button = {'text': shop, 'callback_data': f'shop_{shop}'}
        row.append(button)

        # 3 buttons in the row
        if i % 3 == 0:
            keyboard['inline_keyboard'].append(row)
            row = []

    # if one row left
    if row:
        keyboard['inline_keyboard'].append(row)

    home = {'text': 'В меню', 'callback_data': f'home'}
    keyboard['inline_keyboard'].append([home])

    return keyboard


# for analys updates
def handle_update(update: dict) -> None:
    '''
    :param update: Dictionary (update odject(
    :return: None (return nothing)

    Processes update from Telegram
    '''

    # if message exists in the update
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        # if command was start
        if text == '/start':
            send_message(chat_id, 'Добро пожаловать!')

            show_main_menu(chat_id)

        # if button category was chosen
        elif text == 'Категории':
            show_main_menu(chat_id)

        # if button shop was chosen
        elif text == 'Магазины':
            keyboard = get_shop_keyboard()

            send_message(chat_id, 'Выберите: ', reply_markup=keyboard)

    # if callback query is in update
    elif 'callback_query' in update:
        callback = update['callback_query']
        data = callback['data']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']

        edit_message(chat_id, message_id, text='Рады вас видеть!')

        # if home callback was chosen
        if data == 'home':
            show_main_menu(chat_id)

        # if callback show_shops was chosen
        elif data == 'show_shops':
            keyboard = get_shop_keyboard()
            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        # if category callback was chosen
        elif data.startswith('category_'):
            selected_category = data.replace('category_', '')

            # filtering row of sheet by category of shop
            filtered_row = [row for row in sheet_data if len(row) > 8 and row[8] == selected_category]

            # getting unique shops
            shops = list(set([row[0] for row in filtered_row]))

            # initial keyboard
            keyboard = {'inline_keyboard': []}

            # add shops in the keyboard
            for shop in shops:
                button = {'text': shop, 'callback_data': f'shop_{shop}'}
                keyboard['inline_keyboard'].append([button])

            # add home in the keyboard
            home = {'text': 'В меню', 'callback_data': 'home'}
            keyboard['inline_keyboard'].append([home])

            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        # if shop callback was chosen
        elif data.startswith('shop_'):
            selected_shop = data.replace('shop_', '')

            # filtering row of sheet by shop
            filtered_rows = [row for row in sheet_data if row[0] == selected_shop]

            # getting uniques prom codes
            proms = [row[3] for row in filtered_rows]

            # initial keyboard
            keyboard = {'inline_keyboard': []}
            home = {'text': 'В меню', 'callback_data': 'home'}
            keyboard['inline_keyboard'].append([home])

            # add prom code in the keyboard
            for prom in proms:
                button = {'text': prom, 'callback_data': f'prom_{prom}'}
                keyboard['inline_keyboard'].append([button])

            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        # if prom code callback was chosen
        elif data.startswith('prom_'):
            selected_prom = data.replace('prom_', '')

            # getting prom code from google sheet
            for row in sheet_data:
                if row[3] == selected_prom:
                    discount = row
                    break

            send_message(chat_id, 'Чтобы воспользоваться акцией необходимо: перейти по ссылке '
                                  'или скопировать промокод и ввести его на сайте или '
                                  'приложении магазина')

            # text for sending user
            text = (f'Название: {discount[0]}\n'
                    f'Скидка: {discount[3]}\n'
                    f'Ссылка: {discount[4]}\n'
                    f'Действует до: {discount[5]}\n'
                    f'Регион: {discount[6]}\n'
                    f'Условия акции: {discount[7]}')

            send_message(chat_id, text)

            # initial keyboard
            keyboard = {'inline_keyboard': []}

            # add home in the keyboard
            home = {'text': 'В меню', 'callback_data': 'home'}
            keyboard['inline_keyboard'].append([home])

            # add url of tg channel in the keyboard
            tg_channel = {'text': 'Подпишитесь на канал', 'url': 'https://t.me/skidkinezagorami'}
            keyboard['inline_keyboard'].append([tg_channel])

            send_message(chat_id, 'Куда отправимся за скидками дальше?', reply_markup=keyboard)


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
