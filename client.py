import json
import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, TEXT, ANSWER
from common.utils import send_message, receive_message
from logs.client_log_config import logs
import inspect


log = logging.getLogger('app.client')

MOD = inspect.stack()[0][1].split("/")[-1]


@logs
def validation(data):
    if RESPONSE in data:
        if data[RESPONSE] == 200:
            return f'200: {data[ANSWER]}'
        else:
            log.warning(f'{MOD} - сервер прслал код 400 в функции - "{inspect.stack()[0][3]}"')
            return f'400: {data[ERROR]}'
    raise log.error(f'{MOD} - Ошибка валидации ответа сервера в функции - {inspect.stack()[0][3]}')


@logs
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
        log.error(f'{MOD} - ошибка ввода ip или port в функции - "{inspect.stack()[0][3]}"')
        sys.exit(1)

    connection = socket(AF_INET, SOCK_STREAM)
    connection.connect((ip, port))
    message_out = create_message('Hello server!')
    log.info(f'{MOD} - отправлено ссобщение серверу в функции "{inspect.stack()[0][3]}"')
    send_message(connection, message_out)
    try:
        answer = validation(receive_message(connection))
        print(answer)
        log.info(f'{MOD} - получен ответ сервера в функции "{inspect.stack()[0][3]}"')
    except (ValueError, json.JSONDecodeError):
        log.error(f'{MOD} - не верный формат полученного сообщения в функции - "{inspect.stack()[0][3]}"')


if __name__ == '__main__':
    main()
