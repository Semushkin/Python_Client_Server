'''
3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
Важно: решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем.
'''

words = ['attribute', 'класс', 'функция', 'type']


def convert(words):
    for word in words:
        try:
            word = eval(f'b"{word}"')
        except SyntaxError:
            print(f'слово "{word}" нельзя записать в байтовом типе')


convert(words)

