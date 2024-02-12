import json
import sys
import logging
import argparse
import time
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, TEXT, \
    ANSWER, MESSAGE, NICKNAME, FROM, TO
from common.utils import send_message, receive_message, receive_message2
import logs.client_log_config
from logs.decor import log
import inspect
from threading import Thread


logs_client = logging.getLogger('app.client')

MOD = inspect.stack()[0][1].split("/")[-1]


@log
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


@log
def create_message(action, nickname, text='', to = ''):
    if action == PRESENCE:
        return {ACTION: PRESENCE, NICKNAME: nickname}
    elif action == MESSAGE:
        return {ACTION: MESSAGE, NICKNAME: nickname, TEXT: text, TO: to}


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
    parse.add_argument('-n', default='anonymous', help='nickname', nargs='?')
    namespace = parse.parse_args(sys.argv[1:])
    ip = namespace.i
    port = namespace.p
    status = namespace.s
    if status != 'listen' and status != 'send':
        status = 'listen'
    nickname = namespace.n
    return ip, port, status, nickname


def main():
    i = 1
    ip, port, status, nickname = arg_data()
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


    # Получение подтверждения о подключении
    try:
        answer = validation(receive_message(connection))
        print(answer)
        print('----------------------------------------------')
        logs_client.info(f'{MOD} - получен ответ сервера в функции "{inspect.stack()[0][3]}"')
    except (ValueError, json.JSONDecodeError):
        logs_client.error(f'{MOD} - не верный формат полученного сообщения в функции - "{inspect.stack()[0][3]}"')
    else:
        receiver = Thread(target=message_from_server, args=(connection,NICKNAME))
        receiver.daemon = True
        receiver.start()

        commands = Thread(target=user_commands, args=(connection,nickname))
        commands.daemon =True
        commands.start()

        while True:
            time.sleep(1)
            if receiver.is_alive() and commands.is_alive():
                continue
            break


""
def user_commands(connection, nickname):
    print('----------------'
          'Команды:\n'
          'message - Написать сообщение\n'
          'exit - Выйти\n'
          '----------------')
    while True:
        command = input('Введите команду:')
        if command == 'message':
            to = input('Введите получателя:')
            message = input('Введите сообщение:')
            message = create_message(MESSAGE, nickname, message, to)
            send_message(connection, message)
        elif command == 'exit':
            break

def message_from_server(connection, username):
    while True:
        message = validation(receive_message(connection))
        print(f'\nПолучно сообщение от {message[NICKNAME]}: {message[TEXT]}')


if __name__ == '__main__':
    main()
