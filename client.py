import json
import sys
import logging
import argparse
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, TEXT, \
    ANSWER, MESSAGE, NICKNAME, FROM
from common.utils import send_message, receive_message
import logs.client_log_config
from logs.decor import log
import inspect
from metaclasses import ClientVerifier


class Client(metaclass=ClientVerifier):
    def __init__(self, ip, port, status, nickname):
        self.ip = ip
        self.port = port
        self.status = status
        self.nickname = nickname
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connect_server()

    def connect_server(self):
        try:
            print(f'Параметры запуска: ip = {ip}, port = {port}')
            self.connection.connect((ip, port))
            message_out = self.create_message(PRESENCE)
            send_message(self.connection, message_out)
            logs_client.info(f'{MOD} - отправлено собщение серверу в функции "{inspect.stack()[0][3]}"')
        except:
            print('Ошибка соединения c сервером!!!')
            logs_client.critical(f'{MOD} - Ошибка ссоединения с сервером!!!')
            sys.exit(1)
        try:
            answer = self.validation(receive_message(self.connection))
            print(answer)
            print('----------------------------------------------')
            logs_client.info(f'{MOD} - получен ответ сервера в функции "{inspect.stack()[0][3]}"')
        except (ValueError, json.JSONDecodeError):
            logs_client.error(f'{MOD} - не верный формат полученного сообщения в функции - "{inspect.stack()[0][3]}"')
            print('Ошибка получения ответа от сервера!!!')
            sys.exit(1)
        else:
            if self.status == 'receive':
                self.receive()
            elif self.status == 'send':
                self.send()

    @staticmethod
    def validation(data):
        if RESPONSE in data:
            if data[RESPONSE] == 200:
                return f'{data[RESPONSE]}: Установленно ссоединение с сервером'
            else:
                logs_client.warning(f'{MOD} - сервер прслал код 400 в функции - "{inspect.stack()[0][3]}"')
                return f'400: {data[ERROR]}'
        elif data[ACTION] == MESSAGE:
            return {NICKNAME: data[NICKNAME], TEXT: data[TEXT]}
        raise logs_client.error(f'{MOD} - Ошибка валидации ответа сервера в функции - {inspect.stack()[0][3]}')

    def create_message(self, action, text=''):
        if action == PRESENCE:
            return {ACTION: PRESENCE, NICKNAME: self.nickname}
        elif action == MESSAGE:
            return {ACTION: MESSAGE, NICKNAME: self.nickname, TEXT: text}

    def receive(self):
        while True:
            message = self.validation(receive_message(self.connection))
            print(f'Получно сообщение от {message[NICKNAME]}: {message[TEXT]}')

    def send(self):
        while True:
            text = input('Введите сообщение:\n')
            message = self.create_message(MESSAGE, text)
            print(f'Отправлено сообщение {message}')
            send_message(self.connection, message)
            if text == 'exit':
                break


if __name__ == '__main__':
    logs_client = logging.getLogger('app.client')
    MOD = inspect.stack()[0][1].split("/")[-1]

    parse = argparse.ArgumentParser()
    parse.add_argument('-i', default=DEFAULT_IP, help='IP adress', nargs='?')
    parse.add_argument('-p', default=DEFAULT_PORT, help='PORT', type=int, nargs='?')
    parse.add_argument('-s', default='receive', help='status: "receive" or "send"', nargs='?')
    parse.add_argument('-n', default='anonymous', help='nickname', nargs='?')
    namespace = parse.parse_args(sys.argv[1:])
    ip = namespace.i
    port = namespace.p
    status = namespace.s
    nickname = namespace.n
    Client(ip, port, status, nickname)

