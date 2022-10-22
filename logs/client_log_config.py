import logging
import inspect
import sys
import os

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'reports')

logs = logging.getLogger('app.client')

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_hand = logging.FileHandler(f"{PATH}/app.client.log", encoding='utf-8')
#term_hand = logging.StreamHandler(sys.stderr)
file_hand.setFormatter(formatter)

logs.addHandler(file_hand)
#logs.addHandler(term_hand)
logs.setLevel(logging.DEBUG)


if __name__ == '__main__':
    logs.debug(f'режим отладки - {inspect.stack()[0][1].split("/")[-1]}')