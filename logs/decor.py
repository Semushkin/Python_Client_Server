'''
1. Продолжая задачу логирования, реализовать декоратор @log, который
    определяет имя скрипта (client.py или server.py), который инициировал вызов декорируемой функции;
    по имени скрипта находит имя нужного лог-файла для записи сообщения
    добавляет в сообщение значения аргументов вызываемой функции

2. В декораторе @log реализовать определения функции, из которой была вызвана декорированная.

Например, как в коде, приведённом ниже:
@log
def func_x():
    pass

def main():
    func_x()

функция func_x() вызывается из функции main().
Этот факт необходимо отразить в сообщении лог-файла. Например:
<дата-время> Функция func_x() вызвана из функции main

'''

import logging
import inspect
#import client_log_config

CLIENT_M = 'client.py'
SERVER_M = 'server.py'


logs_client = logging.getLogger('app.client')
logs_server = logging.getLogger('app.server')


def log(func):
    def wrapper(*args, **kwargs):
        received_from = inspect.stack()[1][1].split("/")[-1]
        parent_func = str(inspect.stack()[1][0]).split(' ')[-1][:-1]
        if received_from == CLIENT_M:
            logs_client.info(f'{received_from} - функция "{func.__name__}" вызвана из функции "{parent_func}"')
        elif received_from == SERVER_M:
            logs_server.info(f'{received_from} - функция "{func.__name__}" вызвана из функции "{parent_func}"')
        return func(*args, **kwargs)
    return wrapper
