import requests
import time
import json
import gspread

BOT_TOKEN = '**'
URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
GOOGLE_JSON = r'**.json'
SHEET_URL = '**'


# getting info from sheet
def get_info_from_sheet() -> tuple:
    '''
    :return: Tuple (list of shops by category and list of promocodes)

    Getting information from google sheet
    and adding it to dictionary for convenience of work.
    '''

    try:
        gc = gspread.service_account(filename=GOOGLE_JSON)
        sh = gc.open_by_url(SHEET_URL)
        wrksht = sh.get_worksheet(0)
        sheet_data = wrksht.get_all_values()

        shops = {}
        promocodes = {}
        for row in sheet_data[1:]:
            category = row[8]
            shop = row[0]
            promocode = row[3]

            if category not in shops:
                shops[category] = {}

            if shop not in shops[category]:
                shops[category][shop] = []

            shops[category][shop].append(promocode)

            promocodes[promocode] = {
                'shop': shop,
                'category': category,
                'code': promocode,
                'link': row[4] if len(row) > 4 else '',
                'valid_until': row[5] if len(row) > 5 else '',
                'region': row[6] if len(row) > 6 else '',
                'conditions': row[7] if len(row) > 7 else ''
            }

        return shops, promocodes
    except Exception as e:
        print(f'{e}: Не удается получить данные из таблицы')
        return ()


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


def show_main_menu(chat_id: int, shops: dict) -> None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param shops: Dictionary (list of shops)
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

    send_message(chat_id, 'Выберите действия из меню ниже', reply_markup=reply_keyboard)

    # initial keyboard
    keyboard = {'inline_keyboard': []}

    keyboard['inline_keyboard'].append([
        {'text': 'Магазины', 'callback_data': 'show_shops'}
    ])

    # getting categories of shops
    categories = shops.keys()

    # add all categories in the keyboard
    for category in categories:
        button = {'text': category, 'callback_data': f'category_{category}'}
        keyboard['inline_keyboard'].append([button])

    # add url of google sheet in the keyboard
    keyboard['inline_keyboard'].append([
        {'text': 'Таблица со всеми промокодами', 'url': SHEET_URL}
    ])

    send_message(chat_id, 'Выберите категорию, в которой хотите получить скидку', keyboard)


def get_shop_keyboard(shops: dict) -> dict:
    '''
    :param shops: Dictionary (list of shops)
    :return: Dictionary (keyboard of shops)

    This method for showing shop menu.
    '''

    # initial keyboard
    keyboard = {'inline_keyboard': []}

    # getting shops
    unique_shops = sorted(set(shop for category in shops.values() for shop in category.keys()))

    # add shop in the keyboard
    row = []
    for i, shop in enumerate(unique_shops, 1):
        button = {'text': shop, 'callback_data': f'shop_{shop}'}
        row.append(button)

        # 3 buttons in the row
        if i % 3 == 0:
            keyboard['inline_keyboard'].append(row)
            row = []

    # if one row left
    if row:
        keyboard['inline_keyboard'].append(row)

    keyboard['inline_keyboard'].append([{'text': 'В меню', 'callback_data': 'home'}])

    return keyboard


def show_shop_by_category(chat_id: int, message_id: int, shops: dict, category:str) -> None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param message_id: Integer (id of message)
    :param shops: Dictionary (list of shops)
    :param category: String (name of selected category)
    :return: None (return nothing)

    This method show all shop by category.
    '''

    # get shops by category
    category_data = shops.get(category, {})
    shop_names = sorted(category_data.keys())

    # initial keyboard
    keyboard = {'inline_keyboard': []}

    # add shops in the keyboard
    for shop in shop_names:
        keyboard['inline_keyboard'].append([
            {'text': shop, 'callback_data': f'shop_{shop}'}
        ])

    keyboard['inline_keyboard'].append([
        {'text': 'В меню', 'callback_data': 'home'}
    ])

    edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)


def show_proms_by_shop(chat_id: int, message_id: int, shops: dict, selected_shop: str) -> None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param message_id: Integer (id of message)
    :param shops: Dictionary (list of shops)
    :param selected_shop: String (selected shop)
    :return: None (return nothing)

    This method show all promocodes by shop.
    '''

    # check finding promocodes
    found = False

    # finding promocodes
    for category, shop_dict in shops.items():
        if selected_shop in shop_dict:
            promocodes = shop_dict[selected_shop]
            found = True
            break

    # if promocodes don't find
    if not found or not promocodes:
        edit_message(chat_id, message_id, text='Промокоды не найдены для этого магазина.')
        return

    # initial keyboard
    keyboard = {'inline_keyboard': []}

    # add promocode in the keyboard
    for code in promocodes:
        keyboard['inline_keyboard'].append([
            {'text': code, 'callback_data': f'prom_{code}'}
        ])

    keyboard['inline_keyboard'].append([
        {'text': 'В меню', 'callback_data': 'home'}
    ])

    edit_message(chat_id, message_id, text='Выберите промокод:', reply_markup=keyboard)


def show_promo_code(chat_id: int, promocodes: dict, selected_prom: str) -> None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param promocodes: Dictioanry (list of promocodes)
    :param selected_prom: String (selected promocode)
    :return: None (return nothing)

    This method show info about promocode.
    '''

    # geting promocode
    promo = promocodes.get(selected_prom)

    # if promocode don't find
    if not promo:
        send_message(chat_id, 'Промокод не найден.')
        return

    send_message(chat_id, 'Чтобы воспользоваться акцией необходимо: перейти по ссылке '
                          'или скопировать промокод и ввести его на сайте или '
                          'приложении магазина')

    # text about promocode
    text = (f"Название: {promo['shop']}\n"
            f"Скидка: {promo['code']}\n"
            f"Ссылка: {promo['link']}\n"
            f"Действует до: {promo['valid_until']}\n"
            f"Регион: {promo['region']}\n"
            f"Условия акции: {promo['conditions']}")

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


def handle_update(update: dict, shops: dict, promocodes: dict) -> None:
    '''
    :param update: Dictionary (update odject)
    :param shops: Dictionary (list of shops)
    :param promocodes: Dictionary (list of promocodes)
    :return: None (return nothing)

    Processes update from Telegram
    '''

    # if message exists in the update
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        # if command was start
        if text == '/start':
            send_message(chat_id, 'Добро пожаловать')
            show_main_menu(chat_id, shops)

        # if button category was chosen
        elif text == 'Категории':
            show_main_menu(chat_id, shops)

        # if button shop was chosen
        elif text == 'Магазины':
            keyboard = get_shop_keyboard(shops)

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
            show_main_menu(chat_id, shops)

        # if callback show_shops was chosen
        elif data == 'show_shops':
            keyboard = get_shop_keyboard(shops)
            edit_message(chat_id, message_id, text='Выбирайте:', reply_markup=keyboard)

        # if category callback was chosen
        elif data.startswith('category_'):
            selected_category = data.replace('category_', '')

            show_shop_by_category(chat_id, message_id, shops, selected_category)

        # if shop callback was chosen
        elif data.startswith('shop_'):
            selected_shop = data.replace('shop_', '')

            show_proms_by_shop(chat_id, message_id, shops, selected_shop)


        # if prom code callback was chosen
        elif data.startswith('prom_'):
            selected_prom = data.replace('prom_', '')

            show_promo_code(chat_id, promocodes, selected_prom)


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
    shops, promocodes = get_info_from_sheet()

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
                    handle_update(update, shops, promocodes)
                except Exception as e:
                    # in case of error
                    send_message(chat_id, f'Произошла ошибка: {e}')

            time.sleep(1)


# start bot
start()
