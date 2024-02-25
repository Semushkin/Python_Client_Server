import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, \
    ANSWER, MESSAGE, FROM, NICKNAME, TEXT, TO, EXIT
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import receive_message, send_message
import logging
from logs.decor import log
import logs.server_log_config
import inspect
import argparse
import select
from metaclasses import ServerVerifier
from descriptrs import Port
from threading import Thread
from database_server import DataBase


logs_server = logging.getLogger('app.server')
MOD = inspect.stack()[0][1].split("/")[-1]

@log
def arg_data():
    parse = argparse.ArgumentParser()
    parse.add_argument('-a', default=DEFAULT_IP, help='IP adress', nargs='?')
    parse.add_argument('-p', default=DEFAULT_PORT, help='PORT', type=int, nargs='?')
    namespace = parse.parse_args(sys.argv[1:])
    ip = namespace.a
    port = namespace.p

    return ip, port


class Server(Thread, metaclass=ServerVerifier):
    port = Port()
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.database = DataBase()
        self.clients = []
        self.messages = []
        self.clients_name = dict()  # Список сокетов с именами клиентов. {client_name: client_socket}
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connection.bind((self.ip, self.port))
        print(f'Запущен сервер с праметрами: ip = "{self.ip}", port = {self.port}')
        self.connection.settimeout(0.5)
        self.connection.listen(5)
        # self.run()
        super().__init__()

    def run(self):
        while True:
            try:
                client, client_address = self.connection.accept()
            except OSError:
                pass
            else:
                data = receive_message(client)
                data = self.validation(data)
                if data[RESPONSE] != 400:
                    self.clients_name[data[NICKNAME]] = client
                    print(f'Подключился клиент {data[NICKNAME]}')
                    self.database.client_entry(data[NICKNAME], client_address[0])
                    logs_server.info(f'Установлено соединения с клиентом "{data[NICKNAME]}", с адресом {client_address}')
                    send_message(client, {RESPONSE: 200})  # Отправка 200
                    self.clients.append(client)
                else:
                    logs_server.error(f'Неудачная попытка соединения с клиентом {client}, с адресом {client_address}')
            receive_data_lst = []
            send_data_lst = []
            errors_lst =[]
            try:
                if self.clients:
                    receive_data_lst, send_data_lst, errors_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            # Получение сообщений
            if receive_data_lst:
                for client_m in receive_data_lst:
                    try:
                        data = receive_message(client_m)
                        data = self.validation(data)
                        if data[ACTION] == MESSAGE:
                            self.messages.append((data[NICKNAME], data[TEXT], data[TO]))
                            print(f'Получено сообщение от {data[NICKNAME]} для {data[TO]}')
                            logs_server.info(f'Получено сообщение от клиента {data[NICKNAME]}')
                        elif data[ACTION] == EXIT:
                            print(f'Пользователь {data[NICKNAME]} отключился')
                            logs_server.info(f'Пользователь {data[NICKNAME]} отключился')
                            self.database.client_exit(data[NICKNAME])
                            self.clients.remove(client_m)
                            del self.clients_name[data[NICKNAME]]
                    except Exception as e:
                        logs_server.info(f'{MOD} - Ошибка получения сообщения от {client_m}; Ошибка:{e}')
                        logs_server.info(f'{MOD} - клиент {client_m} отключился')
                        self.database.client_exit(data[NICKNAME])
                        self.clients.remove(client_m)
                        del self.clients_name[data[NICKNAME]]
            # Отправка сообщений
            for message in self.messages:
                if message[2] not in self.clients_name.keys(): # Проверяем, есть ли пользователь с таким Именем
                    continue
                message_to_send = self.create_message(message[0], message[1])
                try:
                    send_message(self.clients_name[message[2]], message_to_send)
                except Exception as e:
                    logs_server.info(f'{MOD} - Ошибка отправки сообщения для {self.clients_name[message[2]]}; Ошибка:{e}')
                    logs_server.info(f'{MOD} - клиент {self.clients_name[message[2]]} отключился')
                    self.database.client_exit(data[NICKNAME])
                    self.clients_name[message[2]].close()
                    del self.clients_name[message[2]]
            self.messages.clear()


    @log
    def validation(self, data):
        if ACTION in data and data[ACTION] == PRESENCE:
            return {RESPONSE: 200, NICKNAME: data[NICKNAME]}
        elif ACTION in data and data[ACTION] == MESSAGE:
            return {ACTION: MESSAGE, NICKNAME: data[NICKNAME], TEXT: data[TEXT], TO: data[TO]}
        elif ACTION in data and data[ACTION] == EXIT:
            return {ACTION: EXIT, NICKNAME: data[NICKNAME]}
        else:
            logs_server.warning(f'{MOD} - клиенту отправлен код 400 в функции - "{inspect.stack()[0][3]}"')
            return {RESPONSE: 400, ERROR: 'Bad Request'}

    @staticmethod
    @log
    def create_message(client_from, text):
        return {
            ACTION: MESSAGE,
            NICKNAME: client_from,
            TEXT: text
        }

    def show_history(self):
        print('-------------------------История--------------------------------')
        data = self.database.get_history()
        if data:
            for item in data:
                print(f'Клиент: {item[0]}; с адресом ip: {item[1]}; вход: {item[2]}')
        else:
            print('Нет истории подключений')
        print('----------------------------------------------------------------')

    def show_active_client(self):
        print('-------------------Пользователи онлайн--------------------------')
        data = self.database.get_active_list()
        if data:
            for item in data:
                print(f'Клиент: {item[0]}; с адресом ip: {item[1]}')
        else:
            print('Нет подключенных пользователей')
        print('----------------------------------------------------------------')

if __name__ == '__main__':
    ip, port = arg_data()
    server = Server(ip, port)
    server.daemon = True
    server.start()

    print('------------------Команды----------------------------')
    print('active - Список пользователей онлайн')
    print('history - История входов пользователей')
    print('exit - Выход')
    print('-------------------------------------------------')

    while True:
        command = input('Введите команду:')
        if command == 'active':
            server.show_active_client()
        elif command == 'history':
            server.show_history()
        elif command == 'exit':
            break



