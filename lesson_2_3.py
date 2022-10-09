'''
3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
YAML-формата. Для этого:

    Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
    третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в
    кодировке ASCII (например, €);
    Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию файла
    с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;
    ВАЖНО: Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
'''

import yaml


FILE = 'file.yaml'
DATA = {
    'list': ['data_1', 'data_2', 'data_3'],
    'integer': 3,
    'dictionary': {
        'data_1': "34€",
        'data_2': "3€",
        'data_3': "45€"
    }
}


def load_data(file, data):
    with open(file, 'w', encoding='utf-8') as f_in:
        yaml.dump(data, f_in, allow_unicode=True, default_flow_style=False, sort_keys=False)
    f_in.close()


def check_data(file):
    with open(file, 'r', encoding='utf-8') as f_out:
        return yaml.load(f_out, Loader=yaml.SafeLoader)


load_data(FILE, DATA)
data = check_data(FILE)
print(data)
print(type(data))