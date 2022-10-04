'''
2. Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом,
а не ручном режиме, с помощью добавления литеры b к текстовому значению, (т.е. ни в коем случае не используя методы
encode, decode или функцию bytes) и определить тип, содержимое и длину соответствующих переменных.
'''

words = ['class', 'function', 'method']


def convert(words):
    for word in words:
        word = eval(f'b"{word}"')
        print(f'{word}, тип данных {type(word)}, длина {len(word)}')


convert(words)
