import logging
import inspect
import sys
import os

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'app.clientapp.log')

logs = logging.getLogger('app.clientapp')

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(message)s")
file_hand = logging.FileHandler(PATH, encoding='utf-8')
file_hand.setFormatter(formatter)

logs.addHandler(file_hand)
logs.setLevel(logging.DEBUG)


if __name__ == '__main__':
    logs.debug(f'режим отладки - {inspect.stack()[0][1].split("/")[-1]}')
