import logging
import inspect
import sys
import os
import logging.handlers

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'reports')
PATH = os.path.join(PATH, 'app.serverapp.log')

logs = logging.getLogger('app.serverapp')

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# file_hand = logging.FileHandler(f"{PATH}/app.clientapp.log", encoding='utf-8')
file_hand = logging.handlers.TimedRotatingFileHandler(PATH,
                                                      encoding='utf8',
                                                      interval=1,
                                                      when='midnight')
file_hand.setFormatter(formatter)

logs.addHandler(file_hand)
logs.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logs.debug(f'режим отладки - {inspect.stack()[0][1].split("/")[-1]}')
