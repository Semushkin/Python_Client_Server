
import json
from common.variables import ENCODING, MAX_DATA_LENGTH


def receive_message(client):
    data = client.recv(MAX_DATA_LENGTH)
    if isinstance(data, bytes):
        data = data.decode(ENCODING)
        data = json.loads(data)
        return data
    raise ValueError


def send_message(sock, data):
    message = json.dumps(data)
    code_message = message.encode(ENCODING)
    sock.send(code_message)
