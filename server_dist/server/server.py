import os.path
import sys
import logging
import inspect
import argparse
import select
import hmac
import configparser
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock
from binascii import hexlify, a2b_base64
from os import urandom

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

from common.variables import (DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE,
                              ERROR, ACTION, MESSAGE, NICKNAME, TEXT, TO,
                              EXIT, GET_CONTACT, ADD_CONTACT, DEL_CONTACT,
                              CONTACTS, CONTACT_NAME, DATA, ACCESS)
from common.utils import receive_message, send_message
from logs.decor import log, login_required
# import logs.server_log_config
from serverapp.server_gui import (MainWindow, HistoryWindow, ConfigWindow,
                                  create_stat_model, create_connections_model,
                                  ClientsWindow, create_clients_list)
from common.metaclasses import ServerVerifier
from common.descriptrs import Port
from serverapp.database_server import DataBase

logs_server = logging.getLogger('app.serverapp')
MOD = inspect.stack()[0][1].split("/")[-1]

new_connection = False
conflag_lock = Lock()


@log
def arg_data():
    """Функция парсинга агуиментов переданных при запуске сервера из консоли"""
    parse = argparse.ArgumentParser()
    parse.add_argument('-a', default=DEFAULT_IP, help='IP adress', nargs='?')
    parse.add_argument('-p', default=DEFAULT_PORT, help='PORT', type=int, nargs='?')
    namespace = parse.parse_args(sys.argv[1:])
    ip = namespace.a
    port = namespace.p

    return ip, port


class Server(Thread, metaclass=ServerVerifier):
    """Главный класс сервера"""
    port = Port()

    def __init__(self, ip, port, database):
        self.ip = ip
        self.port = port
        self.database = database
        self.clients = []
        self.messages = []
        self.clients_name = dict()  # Список сокетов с именами клиентов. {client_name: client_socket}
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.connection.bind((self.ip, self.port))
        print(f'Запущен сервер с праметрами: ip = "{self.ip}", port = {self.port}')
        self.connection.settimeout(0.5)
        self.connection.listen(5)
        super().__init__()

    def run(self):
        """ Основной метод работы сервера"""
        global new_connection
        while True:
            try:
                client, client_address = self.connection.accept()
            except OSError:
                pass
            else:
                data = receive_message(client)
                data = self.validation(data, client)
            receive_data_lst = []
            send_data_lst = []
            errors_lst = []
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
                        data = self.validation(data, client_m)
                        if ACTION in data:
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
                                with conflag_lock:
                                    new_connection = True
                    except Exception as e:
                        logs_server.info(f'{MOD} - Ошибка получения сообщения от {client_m}; Ошибка:{e}')
                        logs_server.info(f'{MOD} - клиент {client_m} отключился')
                        for client in self.clients_name:
                            if self.clients_name[client] == client_m:
                                self.database.client_exit(client)
                                print(f'Клиент {client} отключился')
                                del self.clients_name[client]
                                break
                        self.clients.remove(client_m)
                        with conflag_lock:
                            new_connection = True
            # Отправка сообщений
            for message in self.messages:
                if message[2] not in self.clients_name.keys():  # Проверяем, есть ли пользователь с таким Именем
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
    @login_required
    def validation(self, data, client):
        """Метод валидации сообщений полученных от клиентов"""
        if not data[ACCESS]:
            try:
                send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})
            except OSError:
                client.close()

        global new_connection

        # Подключение клиента
        if ACTION in data and data[ACTION] == PRESENCE:
            if data[NICKNAME] in self.clients_name.keys():
                send_message(client, {RESPONSE: 400, ERROR: 'Пользователь уже подключен'})
                return

            self.authorization(data, client)

        # Обработка сообщения клиента
        elif ACTION in data and data[ACTION] == MESSAGE:
            logs_server.info(f'Получено сообщение от "{data[NICKNAME]}", для {data[TO]}')
            return {ACTION: MESSAGE, NICKNAME: data[NICKNAME], TEXT: data[TEXT], TO: data[TO]}

        #  Клиент выходит
        elif ACTION in data and data[ACTION] == EXIT:
            return {ACTION: EXIT, NICKNAME: data[NICKNAME]}

        elif ACTION in data and data[ACTION] == GET_CONTACT:
            send_message(client, {RESPONSE: 202, CONTACTS: self.database.get_contacts(data[NICKNAME])})
            return data

        elif ACTION in data and data[ACTION] == ADD_CONTACT:
            if self.database.add_contact(data[NICKNAME], data[CONTACT_NAME]):
                send_message(client, {RESPONSE: 200})
            else:
                send_message(client, {RESPONSE: 406})
            return data
        elif ACTION in data and data[ACTION] == DEL_CONTACT:
            if self.database.delete_contact(data[NICKNAME], data[CONTACT_NAME]):
                send_message(client, {RESPONSE: 200})
            else:
                send_message(client, {RESPONSE: 406})
            return data
        else:
            logs_server.warning(f'{MOD} - клиенту отправлен код 400 в функции - "{inspect.stack()[0][3]}"')
            send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})

    def authorization(self, data, client):
        """Метод авторизации клиентов"""
        global new_connection
        # Проверяем есть ли ткой пользователь
        if not self.database.check_client(data[NICKNAME]):
            try:
                send_message(client, {RESPONSE: 400, ERROR: 'Пользователь не зарегистриован'})
                print(f'Пользователь {data[NICKNAME]}:  не зарегистрирован')
            except OSError:
                pass
        else:
            # hash представление
            random_str = hexlify(urandom(64))
            message_out = {
                RESPONSE: 511,
                DATA: random_str.decode('ascii')
            }
            try:
                send_message(client, message_out)
                answer = receive_message(client)
            except OSError:
                client.close()
                print(f'Пользователь {data[NICKNAME]}:  Ошибка отправки хэш авторизации')
                return
            client_digest = a2b_base64(answer[DATA])
            if RESPONSE in answer and answer[RESPONSE] == 511:
                hash = hmac.new(
                    self.database.get_client_by_name(answer[NICKNAME]).password_hash,
                    random_str,
                    'MD5'
                )
                digest = hash.digest()
                if hmac.compare_digest(digest, client_digest):
                    self.clients_name[data[NICKNAME]] = client
                    print(f'Подключился клиент {data[NICKNAME]}')
                    with conflag_lock:
                        new_connection = True
                    ip, port = client.getpeername()
                    self.database.client_entry(data[NICKNAME], ip)
                    send_message(client, {RESPONSE: 200})
                    logs_server.info(f'Установлено соединения с клиентом "{data[NICKNAME]}", с адресом {ip}')
                    self.clients.append(client)
                else:
                    try:
                        send_message(client, {RESPONSE: 400, ERROR: 'Invalid username or password.'})
                        print(f'Пользователь {data[NICKNAME]}:  Не верный пароль')
                    except OSError:
                        client.close()
            else:
                try:
                    send_message(client, {RESPONSE: 400, ERROR: 'Invalid username or password.'})
                except OSError:
                    client.close()

    @staticmethod
    @log
    def create_message(client_from, text):
        """Метод создания текстового сообщения от клиента для клиента"""
        return {
            ACTION: MESSAGE,
            NICKNAME: client_from,
            TEXT: text
        }


if __name__ == '__main__':
    """Запуск сервера"""
    config = configparser.ConfigParser()
    path = os.getcwd()
    config.read(f"{path}/{'server.ini'}")
    database = DataBase()

    ip, port = arg_data()
    server = Server(ip, port, database)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.statusBar().showMessage('Working')

    def connection_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(create_connections_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_clients():
        global clients_list
        clients_list = ClientsWindow(database)
        clients_list.client_table.setModel(create_clients_list(database))
        clients_list.client_table.resizeColumnsToContents()
        clients_list.client_table.resizeRowsToContents()

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['database_path'])
        config_window.db_file.insert(config['SETTINGS']['database_file'])
        config_window.port.insert(config['SETTINGS']['default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['database_path'] = config_window.db_path.text()
        config['SETTINGS']['database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = str(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(connection_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(connection_update)
    main_window.client_btn.triggered.connect(show_clients)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()
