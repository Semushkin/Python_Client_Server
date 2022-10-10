'''
1. Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):

    клиент отправляет запрос серверу;
    сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть реализованы в виде отдельных скриптов,
     содержащих соответствующие функции.

Функции клиента:
сформировать presence-сообщение;
отправить сообщение серверу;
получить ответ сервера;
разобрать сообщение сервера;
параметры командной строки скрипта client.py <addr> [<port>]:

addr — ip-адрес сервера;

port — tcp-порт на сервере, по умолчанию 7777.
'''
import json
import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, TEXT, ANSWER
from common.utils import send_message, receive_message


def validation(data):
    if RESPONSE in data:
        if data[RESPONSE] == 200:
            return f'200: {data[ANSWER]}'
        return f'400: {data[ERROR]}'
    raise ValueError


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
        print('Неверный номер порта')
        sys.exit(1)

    connection = socket(AF_INET, SOCK_STREAM)
    connection.connect((ip, port))
    message_out = create_message('Hello server!')
    send_message(connection, message_out)
    try:
        answer = validation(receive_message(connection))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не верный формат сообщения')


if __name__ == '__main__':
    main()