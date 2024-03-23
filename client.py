import json
import sys
import logging
import argparse
import time
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, TEXT, \
    ANSWER, MESSAGE, NICKNAME, FROM, TO, EXIT, GET_CONTACT, ADD_CONTACT, DEL_CONTACT, TIME, CONTACT_NAME, CONTACTS
from common.utils import send_message, receive_message
import logs.client_log_config
from logs.decor import log
import inspect
from threading import Thread, Lock
from metaclasses import ClientVerifier
from database_client import DataBase
from errors import ServerError

logs_client = logging.getLogger('app.client')
MOD = inspect.stack()[0][1].split("/")[-1]
# thread_lock = Lock()

class Client(Thread, metaclass=ClientVerifier):
    def __init__(self, nickname, connection, database):
        self.nickname = nickname
        self.connection = connection
        self.database = database
        super().__init__()

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
            # return {NICKNAME: data[NICKNAME], TEXT: data[TEXT]}
            self.database.save_history_messages(data[NICKNAME], self.nickname, data[TEXT])
            return f'\nПолучено сообщение от {data[NICKNAME]}: {data[TEXT]}'
        raise logs_client.error(f'{MOD} - Ошибка валидации ответа сервера в функции - {inspect.stack()[0][3]}')

class ClientSender(Client):
    def run(self):
        print('----------------'
              'Команды:\n'
              '"message" - Написать сообщение\n'
              '"contacts" - Раздел контактов\n'
              '"history" - История сообщений\n'
              '"exit" - Выйти\n'
              '----------------')
        while True:
            command = input('Введите команду:')
            if command == 'message':
                to = input('Введите получателя:')
                message = input('Введите сообщение:')
                self.database.save_history_messages(self.nickname, to, message)
                message = create_message(MESSAGE, self.nickname, message, to)
                # self.database.save_history_messages(self.nickname, to, message)
                send_message(self.connection, message)
            elif command == 'contacts':
                print('------------------------------')
                print('"list" - Вывести список контаков')
                print('"add"  - Добавить контакт')
                print('"del"  - Вывести список контаков')
                print('------------------------------')
                command_cont = input('Введите команду для раздела Контактов:')
                if command_cont == 'list':
                    print(f'Список контактов: {self.database.get_contacts()}')
                elif command_cont == 'add':
                    contact = input('Укажите имя нового контакта:')
                    self.database.add_contact(contact)
                    message = create_message(ADD_CONTACT, self.nickname, contact=contact)
                    send_message(self.connection, message)
                elif command_cont == 'del':
                    contact = input('Укажите имя удаляемого контакта:')
                    self.database.delete_contact(contact)
                    message = create_message(DEL_CONTACT, self.nickname, contact=contact)
                    send_message(self.connection, message)
                else:
                    print('Команда не распознана')
            elif command == 'history':
                for item in self.database.get_history_messages():
                    print(item)
                # print(self.database.get_history_messages())
            elif command == 'exit':
                message = create_message(EXIT, self.nickname)
                send_message(self.connection, message)
                break
            else:
                print('Команда не распознана.')


class ClientReceive(Client):
    def run(self):
        while True:
            time.sleep(1)
            message = self.validation(receive_message(self.connection))
            print(message)


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


@log
def create_presence(account_name='Guest'):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        'time': time.time(),
        'user': {
            'account_name': account_name
        }
    }
    #LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

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

def database_refresh(conn, database, nickname):
    get_contacts = create_message(GET_CONTACT, nickname)
    send_message(conn, get_contacts)
    answer = receive_message(conn)

    if RESPONSE in answer:
        if answer[RESPONSE] == 202:
            for contact in answer[CONTACTS]:
                database.add_contact(contact)
        else:
            raise ServerError('Ошибка запроса контактов с сервера')

def main():
    ip, port, status, nickname = arg_data()

    if not nickname:
        nickname = input('Введите имя пользователя: ')

    connection = socket(AF_INET, SOCK_STREAM)

    #  Подключение к серверу
    try:
        print(f'Параметры запуска: ip = {ip}, port = {port}, nikname = {nickname}')
        connection.connect((ip, port))
        message_out = create_message(PRESENCE, nickname)
        send_message(connection, message_out)
        logs_client.info(f'{MOD} - отправлено собщение серверу в функции "{inspect.stack()[0][3]}"')
    except:
        logs_client.critical(f'{MOD} - Ошибка ссоединения с сервером!!!')
        exit(1)

    # Получение подтверждения о подключении
    try:
        answer = receive_message(connection)
        if answer[RESPONSE] == 400:
            print(f'{answer[RESPONSE]}: Ошибка ссоединения с сервером')
            exit(1)
        print(f'{answer[RESPONSE]}. Установлено ссоединение с сервером')
        print('----------------------------------------------')
        logs_client.info(f'{MOD} - получен ответ сервера в функции "{inspect.stack()[0][3]}"')
    except (ValueError, json.JSONDecodeError):
        logs_client.error(f'{MOD} - не верный формат полученного сообщения в функции - "{inspect.stack()[0][3]}"')
        exit(1)
    except ServerError as err:
        print(err.text)
    else:
        database = DataBase(nickname)

        database_refresh(connection, database, nickname)

        receiver = ClientReceive(nickname, connection, database)
        receiver.daemon = True
        receiver.start()

        commands = ClientSender(nickname, connection, database)
        commands.daemon = True
        commands.start()

        while True:
            time.sleep(1)
            if receiver.is_alive() and commands.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
