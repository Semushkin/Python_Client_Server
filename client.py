import json
import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, TEXT, ANSWER
from common.utils import send_message, receive_message
import logs.client_log_config
from logs.decor import log
import inspect


logs_client = logging.getLogger('app.client')

MOD = inspect.stack()[0][1].split("/")[-1]


@log
def validation(data):
    if RESPONSE in data:
        if data[RESPONSE] == 200:
            return f'200: {data[ANSWER]}'
        else:
            logs_client.warning(f'{MOD} - сервер прслал код 400 в функции - "{inspect.stack()[0][3]}"')
            return f'400: {data[ERROR]}'
    raise logs_client.error(f'{MOD} - Ошибка валидации ответа сервера в функции - {inspect.stack()[0][3]}')


@log
def create_message(text):
    return {ACTION: PRESENCE, TEXT: text}


def main():
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
        if port < 1024 or port > 65535:
            raise ValueError
    except IndexError:
        ip = DEFAULT_IP
        port = DEFAULT_PORT
    except ValueError:
        logs_client.error(f'{MOD} - ошибка ввода ip или port в функции - "{inspect.stack()[0][3]}"')
        sys.exit(1)

    connection = socket(AF_INET, SOCK_STREAM)
    connection.connect((ip, port))
    message_out = create_message('Hello server!')
    logs_client.info(f'{MOD} - отправлено собщение серверу в функции "{inspect.stack()[0][3]}"')
    send_message(connection, message_out)
    try:
        answer = validation(receive_message(connection))
        print(answer)
        logs_client.info(f'{MOD} - получен ответ сервера в функции "{inspect.stack()[0][3]}"')
    except (ValueError, json.JSONDecodeError):
        logs_client.error(f'{MOD} - не верный формат полученного сообщения в функции - "{inspect.stack()[0][3]}"')


if __name__ == '__main__':
    main()
