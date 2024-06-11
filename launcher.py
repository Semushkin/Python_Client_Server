import subprocess
import platform
import os
import sys
import signal
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROCESS = []


def launch():
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
            try:
                if platform.system().lower() == 'windows':
                    PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
                    PROCESS.append(subprocess.Popen('python client.py -n Test_1 -pas 123456', creationflags=subprocess.CREATE_NEW_CONSOLE))
                    PROCESS.append(subprocess.Popen('python client.py -n Test_2 -pas 123456', creationflags=subprocess.CREATE_NEW_CONSOLE))
                    PROCESS.append(subprocess.Popen('python client.py -n Test_3 -pas 123456', creationflags=subprocess.CREATE_NEW_CONSOLE))
                else:
                    PROCESS.append(process('server.py'))
                    sleep(0.5)
                    PROCESS.append(process('client.py -n Test_1 -pas 123456'))
                    sleep(0.5)
                    PROCESS.append(process('client.py -n Test_2 -pas 123456'))
                    sleep(0.5)
                    PROCESS.append(process('client.py -n Test_3 -pas 123456'))
            except Exception as err:
                exit(1)
        if request == 'stop':
            while PROCESS:
                proc = PROCESS.pop()
                os.killpg(proc.pid, signal.SIGINT)
        if request == 'exit':
            break


if __name__ == '__main__':
    launch()
