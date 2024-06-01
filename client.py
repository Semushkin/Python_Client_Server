import hmac
import json
import os.path
import sys
import logging
import argparse
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.variables import *
from common.utils import send_message, receive_message
# import logs.client_log_config
from logs.decor import log
import inspect
from threading import Thread, Lock
from metaclasses import ClientVerifier
from database_client import DataBase
from errors import ServerError
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from client_gui import MainWindow, EnterWindow
from Cryptodome.PublicKey import RSA
from hashlib import pbkdf2_hmac
from binascii import hexlify, b2a_base64


logs_client = logging.getLogger('app.client')
MOD = inspect.stack()[0][1].split("/")[-1]
thread_lock = Lock()


class Client(Thread, QObject):
    signal_new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()
    signal_new_contact = pyqtSignal(str)

    def __init__(self, nickname, password, keys, ip, port, database):
        Thread.__init__(self)
        QObject.__init__(self)
        self.nickname = nickname
        self.password = password
        self.keys = keys
        self.ip = ip
        self.port = port
        print(f'Параметры подключения {self.nickname}, {self.ip}, {self.port}')
        self.connect = None
        self.database = database
        # self.connect = self.connection()
        self.connection()
        self.database_refresh()
        self.close_program = False
        # super().__init__()

    def connection(self):
        self.connect = socket(AF_INET, SOCK_STREAM)
        self.connect.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.connect.settimeout(5)

        #Подключение к серверу
        try:
            print(f'Параметры запуска: ip = {self.ip}, port = {self.port}, nikname = {self.nickname}')
            self.connect.connect((self.ip, self.port))



            # message_out = self.create_message(PRESENCE, self.nickname)
            # send_message(connect, message_out)
            # logs_client.info(f'{MOD} - отправлено собщение серверу в функции "{inspect.stack()[0][3]}"')
        except:
            logs_client.critical(f'{MOD} - Ошибка ссоединения с сервером!!!')
            raise ServerError('400: Ошибка ссоединения с сервером')

        password_bytes = self.password.encode('utf-8')
        salt = self.nickname.lower().encode('utf-8')
        password_hash = pbkdf2_hmac('sha512', password_bytes, salt, 10000)
        password_hash_string = hexlify(password_hash)
        public_key = self.keys.publickey().export_key().decode('ascii')

        message_out = {
            ACTION: PRESENCE,
            NICKNAME: nickname,
            PUBLIC_KEY: public_key
        }

        # Получение подтверждения о подключении. Авторизация
        try:
            send_message(self.connect, message_out)
            answer = receive_message(self.connect)

            if RESPONSE in answer:
                if answer[RESPONSE] == 400 :
                    raise ServerError(f'Ошибка авторизации : {answer[ERROR]}')
                elif answer[RESPONSE] == 511:
                    data = answer[DATA]
                    hash = hmac.new(
                        password_hash_string,
                        data.encode('utf-8'),
                        'MD5'
                    )
                    digest = hash.digest()
                    message_out = {
                        ACTION: PRESENCE,
                        RESPONSE: 511,
                        NICKNAME: nickname,
                        DATA: b2a_base64(digest).decode('ascii')
                    }
                    send_message(self.connect, message_out)
                    answer = receive_message(self.connect)
                    if answer[RESPONSE] == 400:
                        raise ServerError(f'Ошибка авторизации : {answer[ERROR]}')

            else:
                raise ServerError(f'Ошибка авторизации. Некорректный ответ сервера')
        except OSError as err:
            raise ServerError(f'Ошибка авторизации : {err}')

        # Получение подтверждения о подключении. Авторизация
        # try:
        #     answer = receive_message(self.connect)
        #     if answer[RESPONSE] == 400:
        #         print(f'{answer[RESPONSE]}: Ошибка ссоединения с сервером')
        #         exit(1)
        #     print(f'{answer[RESPONSE]}. Установлено ссоединение с сервером')
        #     print('----------------------------------------------')
        #     logs_client.info(f'{MOD} - получен ответ сервера в функции "{inspect.stack()[0][3]}"')
        # except (ValueError, json.JSONDecodeError):
        #     logs_client.error(f'{MOD} - не верный формат полученного сообщения в функции - "{inspect.stack()[0][3]}"')
        #     exit(1)
        # except ServerError as err:
        #     print(err.text)
        # # else:
        # #     return connect

    def authorization(self):
        password_bytes = self.password.encode('utf-8')
        salt = self.nickname.lower().encode('utf-8')
        password_hash = pbkdf2_hmac('sha512', password_bytes, salt, 10000)
        password_hash_string = hexlify(password_hash)
        public_key = self.keys.publickey().export_key().decode('ascii')

        message_out = {
            ACTION: PRESENCE,
            NICKNAME: nickname,
            PUBLIC_KEY: public_key
        }

        try:
            send_message(self.connect, message_out)
            answer = receive_message(self.connect)

            if RESPONSE in answer:
                if answer[RESPONSE] == 400 :
                    raise ServerError(f'Ошибка авторизации : {answer[ERROR]}')
                elif answer[RESPONSE] == 511:
                    data = answer[DATA]
                    hash = hmac.new(
                        password_hash_string,
                        data.encode('utf-8'),
                        'MD5'
                    )
                    digest = hash.digest()
                    message_out = {
                        ACTION: PRESENCE,
                        NICKNAME: nickname,
                        DATA: b2a_base64(digest).decode('ascii')
                    }
                    send_message(self.connect, message_out)
            else:
                raise ServerError(f'Ошибка авторизации. Некорректный ответ сервера')
        except OSError as err:
            raise ServerError(f'Ошибка авторизации : {err}')

    def run(self):
        while not self.close_program:
            time.sleep(1)
            with thread_lock:
                try:
                    self.connect.settimeout(1)
                    self.validation(receive_message(self.connect))
                except OSError as err:
                    if not err.errno:
                        pass
                    else:
                        self.close_program = True
                        self.connection_lost.emit()

    @staticmethod
    @log
    def create_message(action, nickname, text='', to='', contact=''):
        if action == PRESENCE:
            return {ACTION: PRESENCE, NICKNAME: nickname}
        elif action == MESSAGE:
            return {ACTION: MESSAGE, NICKNAME: nickname, TEXT: text, TO: to}
        elif action == EXIT:
            return {ACTION: EXIT, NICKNAME: nickname}
        elif action == GET_CONTACT:
            return {ACTION: GET_CONTACT, TIME: time.time(), NICKNAME: nickname}
        elif action == ADD_CONTACT:
            return {ACTION: ADD_CONTACT, CONTACT_NAME: contact, TIME: time.time(), NICKNAME: nickname}
        elif action == DEL_CONTACT:
            return {ACTION: DEL_CONTACT, CONTACT_NAME: contact, TIME: time.time(), NICKNAME: nickname}

    def database_refresh(self):
        get_contacts = self.create_message(GET_CONTACT, self.nickname)
        send_message(self.connect, get_contacts)
        answer = receive_message(self.connect)
        if RESPONSE in answer:
            if answer[RESPONSE] == 202:
                for contact in answer[CONTACTS]:
                    self.database.add_contact(contact)
            else:
                raise ServerError('Ошибка запроса контактов с сервера')

    @log
    def validation(self, data):
        if RESPONSE in data:
            if data[RESPONSE] == 200:
                return f'{data[RESPONSE]}: Выполнено!'
            elif data[RESPONSE] == 406:
                return f'{data[RESPONSE]}: Ошибка Добавления/Удаления контакта'
            elif data[RESPONSE] == 202:
                return f'{data[RESPONSE]}: Добавлен новый контакт'
            else:
                logs_client.warning(f'{MOD} - сервер прслал код 400 в функции - "{inspect.stack()[0][3]}"')
                # return f'400: {data[ERROR]}'
                raise ServerError(f'Ошибка ссоединения с сервером! {data[ERROR]}')
        elif ACTION in data and data[ACTION] == MESSAGE:
            if not self.database.check_contact(data[NICKNAME]):
                # self.add_contact(data[NICKNAME])
                self.signal_new_contact.emit(data[NICKNAME])
            self.database.save_history_messages(data[NICKNAME], self.nickname, data[TEXT])
            self.signal_new_message.emit(data[NICKNAME])
            return f'\nПолучено сообщение от {data[NICKNAME]}: {data[TEXT]}'
        raise logs_client.error(f'{MOD} - Ошибка валидации ответа сервера в функции - {inspect.stack()[0][3]}')

    def add_contact(self, new_contact):
        with thread_lock:
            message_out = self.create_message(ADD_CONTACT, self.nickname, contact=new_contact)
            send_message(self.connect, message_out)
            message_in = receive_message(self.connect)
            if RESPONSE in message_in:
                if message_in[RESPONSE] == 200:
                    self.database.add_contact(new_contact)
                    return True
                else:
                    return False

    def delete_contact(self, del_contact):
        with thread_lock:
            message_out = self.create_message(DEL_CONTACT, self.nickname, contact=del_contact)
            send_message(self.connect, message_out)
            message_in = receive_message(self.connect)
            if RESPONSE in message_in:
                if message_in[RESPONSE] == 200:
                    self.database.delete_contact(del_contact)
                    return True
                else:
                    return False

    def send_message(self, text, contact):
        with thread_lock:
            message = self.create_message(MESSAGE, self.nickname, text, contact)
            send_message(self.connect, message)
            self.database.save_history_messages(self.nickname, contact, text)


@log
def arg_data():
    parse = argparse.ArgumentParser()
    parse.add_argument('-i', default=DEFAULT_IP, help='IP adress', nargs='?')
    parse.add_argument('-p', default=DEFAULT_PORT, help='PORT', type=int, nargs='?')
    parse.add_argument('-s', default='listen', help='status: "listen" or "send"', nargs='?')
    parse.add_argument('-n', help='nickname', nargs='?')
    namespace = parse.parse_args(sys.argv[1:])
    ip = namespace.i
    port = namespace.p
    status = namespace.s
    if status != 'listen' and status != 'send':
        status = 'listen'
    nickname = namespace.n
    return ip, port, status, nickname


if __name__ == '__main__':

    app = QApplication(sys.argv)
    nick_app = EnterWindow()
    app.exec_()
    nickname = nick_app.nickname
    password = nick_app.password
    ip = DEFAULT_IP
    port = DEFAULT_PORT
    # ip = nick_app.address
    # port = nick_app.port
    if not nickname or not password:
        exit(1)
    else:
        print(f'data = {nickname}, {password}')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{nickname}')

    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    # if not ip:
    #     ip = DEFAULT_IP
    # if not port:
    #     port = DEFAULT_PORT
    try:
        database = DataBase(nickname)
        client = Client(nickname, password, keys, ip, port, database)
        client.setDaemon(True)
        client.start()
    except ServerError as e:
        print(f'{e.text}')
        message = QMessageBox()
        message.setWindowTitle('Ошибка!!!')
        message.setText(f'{e.text}')
        message.exec()
    else:
        main_window = MainWindow(database, client)
        app.exec_()


