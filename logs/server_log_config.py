import logging
import inspect
import sys
import os
import logging.handlers

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'reports')
PATH = os.path.join(PATH, 'app.server.log')

log = logging.getLogger('app.server')

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#file_hand = logging.FileHandler(f"{PATH}/app.client.log", encoding='utf-8')
file_hand = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='midnight')
file_hand.setFormatter(formatter)

log.addHandler(file_hand)
log.setLevel(logging.DEBUG)


def logs(func):
    def wrapper(*args, **kwargs):
        log.info(f'{inspect.stack()[1][1].split("/")[-1]} - вызвана функция "{func.__name__}"')
        return func(*args, **kwargs)
    return wrapper


if __name__ == '__main__':
    log.debug(f'режим отладки - {inspect.stack()[0][1].split("/")[-1]}')