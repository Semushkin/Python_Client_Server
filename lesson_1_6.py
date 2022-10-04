'''
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
Далее забыть о том, что мы сами только что создали этот файл и исходить из того, что перед нами файл в неизвестной
кодировке. Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.
'''

from chardet import detect

words = ['сетевое программирование', 'сокет', 'декоратор']
FILE_NAME = 'test_file.txt'


def create_file(file_name, words):
    f = open(file_name, 'w', encoding='utf-8')
    for word in words:
        f.write(f'{word}\n')
    f.close()


def read_file(file_name):
    with open(file_name, 'rb') as f:
        content = f.read()
    encoding = detect(content)['encoding']
    with open(file_name, encoding=encoding) as f:
        for line in f:
            print(line, end='')

create_file(FILE_NAME, words)
read_file(FILE_NAME)
