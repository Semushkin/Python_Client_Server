import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, \
    ANSWER, MESSAGE, FROM, NICKNAME, TEXT
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import receive_message, send_message
import logging
from logs.decor import log
import logs.server_log_config
import inspect
import argparse
import select


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.check_port()
        self.clients = []
        self.messages = []
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connection.bind((self.ip, self.port))
        print(f'Запущен сервер с праметрами: ip = "{self.ip}", port = {self.port}')
        self.connection.settimeout(0.5)
        self.connection.listen(5)
        self.listen()

    def start(self):
        pass

    def check_port(self):
        if self.port < 1027 or self.port > 65535:
            print('Ошибка!!! Не верный номер порта. Должен быть больше 1027 и меньше 65535')
            sys.exit(1)

    def pr(self):
        return f'ip = {self.ip}, port = {self.port}'

    def listen(self):
        while True:
            try:
                client, client_address = self.connection.accept()
            except OSError:
                pass
            else:
                data = self.validation(receive_message(client))
                if data[RESPONSE] != 400:
                    print(f'Подключился клиент {data[NICKNAME]}')
                    logs_server.info(
                        f'Установлено соединения с клиентом "{data[NICKNAME]}", с адресом {client_address}')
                    send_message(client, {RESPONSE: 200})  # Отправка 200
                    self.clients.append(client)
                else:
                    logs_server.error(f'Неудачная попытка соединения с клиентом {client}, с адресом {client_address}')
            self.receive()

    def receive(self):
        receive_data_lst = []
        send_data_lst = []
        errors_lst =[]
        try:
            if self.clients:
                receive_data_lst, send_data_lst, errors_lst = select.select(self.clients, self.clients, [], 0)
        except OSError:
            pass
        if receive_data_lst:
            for client_m in receive_data_lst:
                try:
                    data = receive_message(client_m)
                    data = self.validation(data)
                    if data[ACTION] == MESSAGE:
                        self.messages.append((data[NICKNAME], data[TEXT]))
                        logs_server.info(f'Получено сообщение от клиента {data[NICKNAME]}')
                except:
                    logs_server.info(f'{MOD} - клиент {client_m} отключился, при попытке получения сообщения')
                    self.clients.remove(client_m)

        if self.messages and send_data_lst:
            message = self.create_message(self.messages[0][0], self.messages[0][1])
            del self.messages[0]
            for client_s in send_data_lst:
                logs_server.info(f'получено сообщение от клиента {client_s}: {self.messages}')
                try:
                    send_message(client_s, message)
                except:
                    logs_server.info(f'{MOD} - клиент {client_s} отключился, при попытке отправке сообщения')
                    client_s.close()
                    self.clients.remove(client_s)

    def send_data_lst(self):
        pass

    def validation(self, data):
        if ACTION in data and data[ACTION] == PRESENCE:
            return {RESPONSE: 200, NICKNAME: data[NICKNAME]}
        elif ACTION in data and data[ACTION] == MESSAGE:
            return {ACTION: MESSAGE, NICKNAME: data[NICKNAME], TEXT: data[TEXT]}
        else:
            logs_server.warning(f'{MOD} - клиенту отправлен код 400 в функции - "{inspect.stack()[0][3]}"')
            return {RESPONSE: 400, ERROR: 'Bad Request'}

    def create_message(self, client_from, text):
        return {
            ACTION: MESSAGE,
            NICKNAME: client_from,
            TEXT: text
        }



if __name__ == '__main__':

    logs_server = logging.getLogger('app.server')
    MOD = inspect.stack()[0][1].split("/")[-1]

    parse = argparse.ArgumentParser()
    parse.add_argument('-a', default=DEFAULT_IP, help='IP adress', nargs='?')
    parse.add_argument('-p', default=DEFAULT_PORT, help='PORT', type=int, nargs='?')
    namespace = parse.parse_args(sys.argv[1:])

    serv = Server(namespace.a, namespace.p)