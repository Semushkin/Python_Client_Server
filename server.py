import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, \
    ANSWER, MESSAGE, FROM, NICKNAME, TEXT, TO
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import receive_message, send_message
import logging
from logs.decor import log
import logs.server_log_config
import inspect
import argparse
import select


logs_server = logging.getLogger('app.server')
MOD = inspect.stack()[0][1].split("/")[-1]


@log
def validation(data):
    if ACTION in data and data[ACTION] == PRESENCE:
        return {RESPONSE: 200, NICKNAME: data[NICKNAME]}
    elif ACTION in data and data[ACTION] == MESSAGE:
        return {ACTION: MESSAGE, NICKNAME: data[NICKNAME], TEXT: data[TEXT], TO: data[TO]}
    else:
        logs_server.warning(f'{MOD} - клиенту отправлен код 400 в функции - "{inspect.stack()[0][3]}"')
        return {RESPONSE: 400, ERROR: 'Bad Request'}


@log
def arg_data():
    parse = argparse.ArgumentParser()
    parse.add_argument('-a', default=DEFAULT_IP, help='IP adress', nargs='?')
    parse.add_argument('-p', default=DEFAULT_PORT, help='PORT', nargs='?')
    namespace = parse.parse_args(sys.argv[1:])
    ip = namespace.a
    port = namespace.p

    if port < 1027 or port > 65535:
        logs_server.error(f'{MOD} - Указан не верный номер порта при запуске сервера')
        sys.exit(1)
    return ip, port


@log
def create_message(client_from, text):
    return {
        ACTION: MESSAGE,
        NICKNAME: client_from,
        TEXT: text
    }


def main():
    ip, port = arg_data()
    clients = []
    messages = []
    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((ip, port))
    print(f'Запущен сервер с праметрами: ip = "{ip}", port = {port}')
    connection.settimeout(0.5)
    connection.listen(5)

    clients_name = dict() # Список сокетов с именами клиентов. {client_name: client_socket}

    while True:
        try:
            client, client_address = connection.accept()
        except OSError:
            pass
        else:
            data = receive_message(client)
            data = validation(data)
            if data[RESPONSE] != 400:
                clients_name[data[NICKNAME]] = client
                print(f'Подключился клиент {data[NICKNAME]}')
                logs_server.info(f'Установлено соединения с клиентом "{data[NICKNAME]}", с адресом {client_address}')
                send_message(client, {RESPONSE: 200})  # Отправка 200
                clients.append(client)
            else:
                logs_server.error(f'Неудачная попытка соединения с клиентом {client}, с адресом {client_address}')

        receive_data_lst = []
        send_data_lst = []
        errors_lst =[]
        try:
            if clients:
                receive_data_lst, send_data_lst, errors_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass
        # Получение сообщений
        if receive_data_lst:
            for client_m in receive_data_lst:
                try:
                    data = receive_message(client_m)
                    data = validation(data)
                    if data[ACTION] == MESSAGE:
                        messages.append((data[NICKNAME], data[TEXT], data[TO]))
                        print(f'Получено сообщение от {data[NICKNAME]} для {data[TO]}')
                        logs_server.info(f'Получено сообщение от клиента {data[NICKNAME]}')
                except Exception as e:
                    logs_server.info(f'{MOD} - Ошибка получения сообщения от {client_m}; Ошибка:{e}')
                    logs_server.info(f'{MOD} - клиент {client_m} отключился')
                    clients.remove(client_m)
                    del clients_name[data[NICKNAME]]
        # Отправка сообщений
        for message in messages:
            if message[2] not in clients_name.keys(): # Проверяем, есть ли пользователь с таким Именем
                continue
            message_to_send = create_message(message[0], message[1])
            try:
                send_message(clients_name[message[2]], message_to_send)
            except Exception as e:
                logs_server.info(f'{MOD} - Ошибка отправки сообщения для {clients_name[message[2]]}; Ошибка:{e}')
                logs_server.info(f'{MOD} - клиент {clients_name[message[2]]} отключился')
                clients_name[message[2]].close()
                del clients_name[message[2]]
        messages.clear()

if __name__ == '__main__':
    main()
