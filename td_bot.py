import requests
import time

TOKEN = '*****'
URL = f'https://api.telegram.org/bot{TOKEN}'
OPERATORS = '+-/*='


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
def send_message(chat_id: int, text: str) -> dict | None:
    '''
    :param chat_id: Integer (id of chat for sending messages)
    :param text: String (message text for sending)
    :return: Dictionary | None (response from Telegram server, or None in case of error)

    Send text message to user.
    '''

    try:
        # request params
        params = {'chat_id': chat_id, 'text': text}
        resp = requests.get(URL + '/sendMessage', params=params)

        # check request status
        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException as e:
        # in case of error
        return None


# calculator
def calculator(chat_id, text, step, result, oper) -> tuple:
    '''
    :param chat_id: Integer (id of chat for sending message)
    :param text: String (message text for sending)
    :param step: Integer (interaction user step)
    :param result: Float (current user result)
    :param oper: String (current user operator)
    :return: Tuple (list of current user state)

    Simple calculator functional.
    Support operations: addition, subtraction, multiplication, division.
    Entering "=" displays the current result.
    '''

    try:
        if step == 0:
            send_message(chat_id, 'Введите число: ')
            step = 1
        elif step == 1:
            try:
                num1 = float(text)

                # if it is first num, save as result
                if result is None:
                    result = num1
            except ValueError:
                # if incorrect input
                send_message(chat_id, 'Некорректный ввод!')
                send_message(chat_id, 'Введите число: ')

                return step, result, oper

            # if operator exists, calculate result
            if oper == '+':
                result += num1
            elif oper == '-':
                result -= num1
            elif oper == '*':
                result *= num1
            elif oper == '/':
                if num1 == 0:
                    raise ZeroDivisionError('На ноль делить нельзя!')
                result /= num1

            # request for new operator
            send_message(chat_id, 'Введите оператор (+, -, *, /, =): ')
            step = 2
        elif step == 2:
            # if the operator is correct
            if text not in OPERATORS:
                raise ValueError('Неверный оператор!')

            if text == '=':
                # show result
                send_message(chat_id, f'Результат: {result}')

                # reset state
                result = None
                oper = None
                send_message(chat_id, 'Введите число:')
                step = 1
            else:
                # save operator
                oper = text

                # request for new number
                send_message(chat_id, 'Введите число:')
                step = 1
    # if an incorrect operator was entered
    except ValueError as e:
        send_message(chat_id, 'Неверный оператор!')
        send_message(chat_id, 'Введите оператор:')

        return step, result, oper
    # if zero division was happened
    except ZeroDivisionError as e:
        send_message(chat_id, str(e))
        step = 1
        send_message(chat_id, 'Введите число:')

    return step, result, oper


# start bot
def start() -> None:
    '''
    :return: None (return nothing)

    Start Telegram-bot with using long polling.
    '''

    # for receiving new message
    offset: int | None = None

    # all users states
    user_states: dict[int, dict] = {}

    while True:
        # get new updates
        updates = get_updates(offset)

        # if there is some update
        if 'result' in updates:
            for update in updates['result']:
                # save offset
                offset = update['update_id'] + 1

                # get message
                message = update.get('message', {})
                # get message text
                text = message.get('text', '')
                # get message chat id
                chat_id = message['chat']['id']

                # get current user state
                state = user_states.get(chat_id, {
                    'step': 0,
                    'result': None,
                    'oper': None
                })

                try:
                    # perform calculating for particular user
                    step, result, oper = calculator(
                        chat_id, text, state['step'], state['result'], state['oper']
                    )

                    # save particular user information
                    user_states[chat_id] = {
                        'step': step,
                        'result': result,
                        'oper': oper
                    }

                # some other exceptions
                except Exception as e:
                    send_message(chat_id, f'Ошибка: {e}')
                    send_message(chat_id, 'Введите число:')
                    step = 1

                # delay before next request
                time.sleep(1)


# start bot
start()
