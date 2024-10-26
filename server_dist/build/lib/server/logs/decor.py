import logging
import inspect
from socket import socket
# import client_log_config
import logs.client_log_config

CLIENT_M = 'clientapp.py'
SERVER_M = 'serverapp.py'


logs_client = logging.getLogger('app.clientapp')
logs_server = logging.getLogger('app.serverapp')


def log(func):
    """Декоратор. Производит логирования совершенных действий на стороне сервера и пользователя """
    def wrapper(*args, **kwargs):
        received_from = inspect.stack()[1][1].split("/")[-1]
        parent_func = str(inspect.stack()[1][0]).split(' ')[-1][:-1]
        if received_from == CLIENT_M:
            logs_client.info(f'{received_from} - функция "{func.__name__}" вызвана из функции "{parent_func}"')
        elif received_from == SERVER_M:
            logs_server.info(f'{received_from} - функция "{func.__name__}" вызвана из функции "{parent_func}"')
        return func(*args, **kwargs)
    return wrapper


def login_required(func):
    """Декоратор. Проверяет, является ли пользователь авторизованным. """
    from common.variables import ACTION, PRESENCE, NICKNAME, ACCESS

    def wrapper(*args, **kwargs):
        args[1][ACCESS] = False
        if isinstance(args[2], socket):
            if args[1].get(ACTION) == PRESENCE:
                args[1][ACCESS] = True
            elif args[1].get(NICKNAME) and args[1].get(NICKNAME) in args[0].clients_name:
                args[1][ACCESS] = True
        return func(*args, **kwargs)
    return wrapper
