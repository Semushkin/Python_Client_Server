import subprocess
import platform
from time import sleep
import os
import sys
import signal

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROCESS = []


def process(file_with_args):
    sleep(0.2)
    file_full_path = f"{PYTHON_PATH} {BASE_PATH}/{file_with_args}"
    args = ["gnome-terminal", "--disable-factory", "--", "bash", "-c", file_full_path]
    return subprocess.Popen(args, preexec_fn=os.setpgrp)


while True:
    request = input('Введите команду:\n'
                    'start - запустить сервер и клиента\n'
                    'stop - остановить сервер и клиента\n'
                    'exit - Выйти\n')

    if request == 'start':
        if platform.system().lower() == 'windows':
            PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen('python client.py -s send', creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen('python client.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        else:
            PROCESS.append(process('server.py'))
            sleep(0.5)
            PROCESS.append(process('client.py -s send'))
            sleep(0.5)
            PROCESS.append(process('client.py'))
            sleep(0.5)
            PROCESS.append(process('client.py'))
    if request == 'stop':
        while PROCESS:
            print('del')
            proc = PROCESS.pop()
            os.killpg(proc.pid, signal.SIGINT)
    if request =='exit':
        break
