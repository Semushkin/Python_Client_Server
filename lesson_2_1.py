'''
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных
из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:

    Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание
    данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
    «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
    соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
    os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
    поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
    «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для
    каждого файла);

    Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
    данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;

    Проверить работу программы через вызов функции write_to_csv().
'''

import csv
import re
from chardet import detect

FILES_NAMES = ['info_1.txt', 'info_2.txt', 'info_3.txt']
FILE_MAIN = 'main_data.csv'

COLUMNS = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']

os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []
main_data = []


def get_data(files_names, columns):

    for file_name in files_names:

        with open(file_name, 'rb') as f:
            data = f.read()
        data_code = detect(data)['encoding']

        with open(file_name, encoding=data_code) as f:
            text = f.read()

            pattern = re.compile(eval(f"r'{columns[0]}.+'"))
            result = ((re.findall(pattern, text)[0])[len(columns[0])+1:]).strip()
            os_prod_list.append(result)

            pattern = re.compile(eval(f"r'{columns[1]}.+'"))
            result = ((re.findall(pattern, text)[0])[len(columns[1])+1:]).strip()
            os_name_list.append(result)

            pattern = re.compile(eval(f"r'{columns[2]}.+'"))
            result = ((re.findall(pattern, text)[0])[len(columns[2])+1:]).strip()
            os_code_list.append(result)

            pattern = re.compile(eval(f"r'{columns[3]}.+'"))
            result = ((re.findall(pattern, text)[0])[len(columns[3])+1:]).strip()
            os_type_list.append(result)

    main_data.append(columns)
    main_data.append(os_prod_list)
    main_data.append(os_name_list)
    main_data.append(os_code_list)
    main_data.append(os_type_list)

    return main_data


def write_to_csv(files_target, columns, file_main):
    data = get_data(files_target, columns)
    load_data = []

    load_data.append(data[0])
    for row in range(0, len(data[1])):
        new_data = []
        for col in range(1, 5):
            new_data.append(data[col][row])
        load_data.append(new_data)

    print('--------------------------------------------------------------')
    with open(file_main, 'w', encoding='utf-8') as f:
        F_WRITER = csv.writer(f)
        for row in load_data:
            F_WRITER.writerow(row)


write_to_csv(FILES_NAMES, COLUMNS, FILE_MAIN)


