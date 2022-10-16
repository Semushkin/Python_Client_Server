'''
Функции сервера:
принимает сообщение клиента;
формирует ответ клиенту;
отправляет ответ клиенту;

имеет параметры командной строки:
-p <port> — TCP-порт для работы (по умолчанию использует 7777);
-a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
'''
import json
import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, ANSWER
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import receive_message, send_message


def validation(data):
    if ACTION in data and data[ACTION] == PRESENCE:
        return {RESPONSE: 200, ANSWER: 'Hello Client'}
    return {RESPONSE: 400, ERROR: 'Bad Request'}


def main():

    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            port = DEFAULT_PORT
        if port < 1027 or port > 65535:
            raise IndexError
    except IndexError:
        print('Указан не верный номер порта')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            ip = sys.argv[sys.argv.index('-a') + 1]
        else:
            ip = DEFAULT_IP
    except IndexError:
        print('Указан не верный ip адрес')
        sys.exit(1)

    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((ip, port))

    connection.listen(5)

    while True:
        client, client_address = connection.accept()
        try:
            data = receive_message(client)
            print(data)
            message = validation(data)
            send_message(client, message)
            client.close()
        except ValueError:
            print('Получено некорректное сообщение')
            client.close()


if __name__ == '__main__':
    main()
