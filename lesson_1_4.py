'''
4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
байтовое и выполнить обратное преобразование (используя методы encode и decode).
'''

words = ['разработка', 'администрирование', 'protocol', 'standard']


def convert_in(words):
    result = []
    for word in words:
        result.append(str.encode(word))
    return result


def convert_out(words):
    result = []
    for word in words:
        result.append(bytes.decode(word))
    return result


print('-----------------------------------------')
print(f'Изначальные данные: {words}')
print('-----------------------------------------')
words = convert_in(words)
print(f'Данные закодированы: {words}')
print('-----------------------------------------')
words = convert_out(words)
print(f'Данные разкодированы: {words}')
print('-----------------------------------------')
