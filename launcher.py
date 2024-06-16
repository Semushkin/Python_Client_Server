import subprocess
import platform
import os
import sys
import signal
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
process = []


def launch():
    def linux_process(file_with_args):
        sleep(0.2)
        file_full_path = f"{PYTHON_PATH} {BASE_PATH}/{file_with_args}"
        args = ["gnome-terminal", "--disable-factory", "--", "bash", "-c", file_full_path]
        return subprocess.Popen(args, preexec_fn=os.setpgrp)

    def stop_process():
        pass

    os.system('cls')
    while True:
        request = input('Введите команду:\n'
                        'start - запустить сервер и клиента\n'
                        'stop - остановить сервер и клиента\n'
                        'exit - Выйти\n')

        if request == 'start':
            if platform.system().lower() == 'windows':
                process.append(subprocess.Popen('python server.py',
                                                creationflags=subprocess.CREATE_NEW_CONSOLE))
                process.append(subprocess.Popen('python client.py -n Test_1 -pas 123456',
                                                creationflags=subprocess.CREATE_NEW_CONSOLE))
                process.append(subprocess.Popen('python client.py -n Test_2 -pas 123456',
                                                creationflags=subprocess.CREATE_NEW_CONSOLE))
                process.append(subprocess.Popen('python client.py -n Test_3 -pas 123456',
                                                creationflags=subprocess.CREATE_NEW_CONSOLE))
            else:
                process.append(linux_process('server.py'))
                sleep(0.5)
                process.append(linux_process('client.py -n Test_1 -pas 123456'))
                sleep(0.5)
                process.append(linux_process('client.py -n Test_2 -pas 123456'))
                sleep(0.5)
                process.append(linux_process('client.py -n Test_3 -pas 123456'))
        if request == 'stop':
            while process:
                # proc = PROCESS.pop()
                # os.killpg(proc.pid, signal.SIGINT)
                process.pop().kill()
        if request == 'exit':
            break
        os.system('cls')


if __name__ == '__main__':
    launch()
