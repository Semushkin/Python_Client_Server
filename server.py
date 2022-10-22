import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP, PRESENCE, RESPONSE, ERROR, ACTION, ANSWER
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import receive_message, send_message
import logging
from logs.decor import log
import logs.server_log_config
import inspect


logs_server = logging.getLogger('app.server')
MOD = inspect.stack()[0][1].split("/")[-1]


@log
def validation(data):
    if ACTION in data and data[ACTION] == PRESENCE:
        return {RESPONSE: 200, ANSWER: 'Hello Client'}
    else:
        logs_server.warning(f'{MOD} - клиенту отправлен код 400 в функции - "{inspect.stack()[0][3]}"')
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
        logs_server.error(f'{MOD} - указан не верный номер порта в функции - "{inspect.stack()[0][3]}"')
        #print('Указан не верный номер порта')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            ip = sys.argv[sys.argv.index('-a') + 1]
        else:
            ip = DEFAULT_IP
    except IndexError:
        logs_server.error(f'{MOD} - указан не верный ip адрес в функции - "{inspect.stack()[0][3]}"')
        #print('Указан не верный ip адрес')
        sys.exit(1)

    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((ip, port))

    connection.listen(5)

    while True:
        client, client_address = connection.accept()
        try:
            data = receive_message(client)
            print(data)
            logs_server.info(f'{MOD} - получено сообщение от клиента в функции - "{inspect.stack()[0][3]}"')
            message = validation(data)
            send_message(client, message)
            logs_server.info(f'{MOD} - отпрален ответ клиенту в функции - "{inspect.stack()[0][3]}"')
            client.close()
        except ValueError:
            logs_server.error(f'{MOD} - получено некорректное сооьщение от клиента в функции - "{inspect.stack()[0][3]}"')
            #print('Получено некорректное сообщение')
            client.close()


if __name__ == '__main__':
    main()
