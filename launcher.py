import subprocess
import platform


PROCESS = []


while True:
    request = input('Введите команду:\n'
                    'start - запустить сервер и клиента\n'
                    'stop - остановить сервер и клиента\n'
                    'exit - Выйти\n')

    if request == 'start':
        if platform.system().lower() == 'windows':
            PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen('python client.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        else:
            PROCESS.append(subprocess.Popen('python3 server.py', shell=True))
            PROCESS.append(subprocess.Popen('python3 client.py', shell=True))
    if request == 'stop':
        while PROCESS:
            proc = PROCESS.pop()
            proc.kill()
    if request =='exit':
        break

    #print('Введена не верная команда')
