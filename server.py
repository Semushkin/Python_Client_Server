import os.path
import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, \
    ANSWER, MESSAGE, FROM, NICKNAME, TEXT, TO, EXIT, GET_CONTACT, ADD_CONTACT, DEL_CONTACT, CONTACTS, CONTACT_NAME
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
from threading import Thread, Lock
from database_server import DataBase
from PyQt5.QtWidgets import QApplication, QMessageBox
from server_gui import (MainWindow, HistoryWindow, ConfigWindow, create_stat_model, create_connections_model,
                        ClientsWindow, create_clients_list)
import configparser
from PyQt5.QtCore import QTimer

logs_server = logging.getLogger('app.server')
MOD = inspect.stack()[0][1].split("/")[-1]

new_connection = False
conflag_lock = Lock()

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
    def __init__(self, ip, port, database):
        self.ip = ip
        self.port = port
        #self.database = DataBase()
        self.database = database
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
        global new_connection
        while True:
            try:
                client, client_address = self.connection.accept()
            except OSError:
                pass
            else:
                data = receive_message(client)
                data = self.validation(data, client)
                # if data[RESPONSE] != 400:
                #     self.clients_name[data[NICKNAME]] = client
                #     print(f'Подключился клиент {data[NICKNAME]}')
                #     with conflag_lock:
                #         new_connection = True
                #     self.database.client_entry(data[NICKNAME], client_address[0])
                #     logs_server.info(f'Установлено соединения с клиентом "{data[NICKNAME]}", с адресом {client_address}')
                #     send_message(client, {RESPONSE: 200})  # Отправка 200
                #     self.clients.append(client)
                # else:
                #     logs_server.error(f'Неудачная попытка соединения с клиентом {client}, с адресом {client_address}')
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
                        self.database.client_exit(data[NICKNAME])
                        self.clients.remove(client_m)
                        del self.clients_name[data[NICKNAME]]
                        with conflag_lock:
                            new_connection = True
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
    def validation(self, data, client):
        global new_connection
        if ACTION in data and data[ACTION] == PRESENCE:
            if data[NICKNAME] in self.clients_name.keys():
                send_message(client, {RESPONSE: 400, ERROR: 'Nickname has already been registered'})
                return
            self.clients_name[data[NICKNAME]] = client
            print(f'Подключился клиент {data[NICKNAME]}')
            with conflag_lock:
                new_connection = True
            ip, port = client.getpeername()
            self.database.client_entry(data[NICKNAME], ip)
            send_message(client, {RESPONSE: 200})
            logs_server.info(f'Установлено соединения с клиентом "{data[NICKNAME]}", с адресом {ip}')
            self.clients.append(client)
            # return {RESPONSE: 200, NICKNAME: data[NICKNAME]}
        elif ACTION in data and data[ACTION] == MESSAGE:
            logs_server.info(f'Получено сообщение от "{data[NICKNAME]}", для {data[TO]}')
            return {ACTION: MESSAGE, NICKNAME: data[NICKNAME], TEXT: data[TEXT], TO: data[TO]}
        elif ACTION in data and data[ACTION] == EXIT:
            return {ACTION: EXIT, NICKNAME: data[NICKNAME]}
        elif ACTION in data and data[ACTION] == GET_CONTACT:
            send_message(client, {RESPONSE: 202, CONTACTS: self.database.get_contacts(data[NICKNAME])})
            # return {RESPONSE: 202, 'alert': self.database.get_contacts(data[NICKNAME])}
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
            # return {RESPONSE: 400, ERROR: 'Bad Request'}

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

    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
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
        clients_list = ClientsWindow()
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
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)


    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
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



