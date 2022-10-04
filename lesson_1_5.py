'''
5. Написать код, который выполняет пинг веб-ресурсов yandex.ru, youtube.com и преобразовывает результат из
байтовового типа данных в строковый без ошибок для любой кодировки операционной системы.
'''

import locale
import platform
import subprocess

param = '-n' if platform.system().lower() == 'windows' else '-c'
coding_type = locale.getpreferredencoding()
sites = ['yandex.ru', 'youtube.com']


def convert(site):
    args = ['ping', param, '1', site]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    print(f'Пинг сайта {site}:')
    for line in process.stdout:
        result = line.decode(coding_type).replace('\n', '')
        print(f'incoding: {result}, тип данных {type(result)}')


for site in sites:
    convert('yandex.ru')
    print('---------------------------------------')
