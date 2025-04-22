import requests
import time

TOKEN = '*****'
URL = f'https://api.telegram.org/bot{TOKEN}'
OPERATORS = '+-/*'


def get_updates(offset=None):
    try:
        params = {'timeout': 100, 'offset': offset}
        resp = requests.get(URL + '/getUpdates', params=params)

        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException as e:
        return {'result': []}


def send_message(chat_id, text):
    try:
        params = {'chat_id': chat_id, 'text': text}
        resp = requests.get(URL + '/sendMessage', params=params)

        resp.raise_for_status()

        return resp.json()
    except requests.exceptions.RequestException as e:
        return None


def calculator():
    offset = None
    step = 0
    num1 = None
    oper = None

    while True:
        updates = get_updates(offset)

        if 'result' in updates:
            for update in updates['result']:
                offset = update['update_id'] + 1
                message = update.get('message', {})
                text = message.get('text', '')
                chat_id = message['chat']['id']

                try:
                    if step == 0:
                        send_message(chat_id, "Введите первое число:")
                        step = 1
                    elif step == 1:
                        try:
                            num1 = float(text)
                        except ValueError:
                            send_message(chat_id, "Некорректный ввод!")
                            send_message(chat_id, "Введите первое число:")

                            step = 1

                            continue

                        send_message(chat_id, 'Введите оператор (+, -, *, /): ')
                        step = 2
                    elif step == 2:
                        if text not in OPERATORS:
                            raise ValueError('Неверный оператор!')

                        oper = text
                        send_message(chat_id, 'Введите второе число: ')
                        step = 3

                    elif step == 3:
                        try:
                            num2 = float(text)
                        except ValueError:
                            send_message(chat_id, "Некорректный ввод!")
                            send_message(chat_id, "Введите второе число:")

                            step = 3

                            continue

                        if oper == '+':
                            result = num1 + num2
                        elif oper == '-':
                            result = num1 - num2
                        elif oper == '*':
                            result = num1 * num2
                        elif oper == '/':
                            if num2 == 0:
                                raise ZeroDivisionError("Делить на ноль нельзя")
                            result = num1 / num2

                        send_message(chat_id, f'Результат: {result}')
                        send_message(chat_id, "Введите первое число:")
                        step = 1
                except ValueError as e:
                    send_message(chat_id, f"{e}")
                    send_message(chat_id, "Введите оператор:")
                    step = 2
                except ZeroDivisionError as e:
                    send_message(chat_id, f"{e}")
                    send_message(chat_id, "Введите второе число:")
                    step = 3
                except Exception as e:
                    send_message(chat_id, f"Ошибка: {e}")
                    send_message(chat_id, "Введите первое число:")
                    step = 1

                time.sleep(1)


calculator()
