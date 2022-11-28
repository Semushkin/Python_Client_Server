'''
1. Реализовать метакласс ClientVerifier, выполняющий базовую проверку класса «Клиент» (для некоторых проверок уместно
    использовать модуль dis):

    отсутствие вызовов accept и listen для сокетов;
    использование сокетов для работы по TCP;
    отсутствие создания сокетов на уровне классов, то есть отсутствие конструкций такого вида: class Client: s = socket() ...

2. Реализовать метакласс ServerVerifier, выполняющий базовую проверку класса «Сервер»:

    отсутствие вызовов connect для сокетов;
    использование сокетов для работы по TCP.

'''

from pprint import pprint
import dis


class ClientVerifier(type):
    def __init__(cls, class_name, class_parents, class_attrs):
        sock = False
        for attr in class_attrs:
            try:
                ret = dis.get_instructions(class_attrs[attr])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.argval == 'listen':
                        raise TypeError('Исползован недопустимый метод "listen"')
                    if i.argval == 'accept':
                        raise TypeError('Исползован недопустимый метод "accept"')
                    elif i.argval == 'socket':
                        sock = True
        if not sock:
            raise TypeError('Отсутсвует обязательный модуль "socket"')
        super(ClientVerifier, cls).__init__(class_name, class_parents, class_attrs)



class ServerVerifier(type):
    def __init__(cls, class_name, class_parents, class_attrs):
        sock = False
        for attr in class_attrs:
            try:
                ret = dis.get_instructions(class_attrs[attr])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.argval == 'connect':
                        raise TypeError('Исползован недопустимый метод "connect"')
                    elif i.argval == 'socket':
                        sock = True
        if not sock:
            raise TypeError('Отсутсвует обязательный модуль "socket"')
        super(ServerVerifier, cls).__init__(class_name, class_parents, class_attrs)


