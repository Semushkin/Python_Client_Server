
import json
import sys
sys.path.append('../')
from common.variables import ENCODING, MAX_DATA_LENGTH


def receive_message(client):
    """Функция получения сообщения в формате byte и его преобразования в формат JSON"""
    data = client.recv(MAX_DATA_LENGTH)
    if isinstance(data, bytes):
        data = data.decode(ENCODING)
        data = json.loads(data)
        return data
    raise ValueError


def send_message(sock, data):
    """Функция преобразования сообщения из формата JSON в формат byte и его отправки в сокет"""
    message = json.dumps(data)
    code_message = message.encode(ENCODING)
    sock.send(code_message)
