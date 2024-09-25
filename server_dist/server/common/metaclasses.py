import dis


class ClientVerifier(type):
    """Метакласс клиента, проверяющий отсутсвие недопучтимых методов (listen, accept, socket)"""
    def __init__(cls, class_name, class_parents, class_attrs):
        for attr in class_attrs:
            try:
                ret = dis.get_instructions(class_attrs[attr])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.argval == 'listen':
                        raise TypeError('Исползован недопустимый метод "listen"')
                    elif i.argval == 'accept':
                        raise TypeError('Исползован недопустимый метод "accept"')
                    elif i.argval == 'socket':
                        raise TypeError('Исползован недопустимый метод "socket"')
        super(ClientVerifier, cls).__init__(class_name, class_parents, class_attrs)


class ServerVerifier(type):
    """Метакласс сервера, проверяющий отсутсвие недопумтимого метода connect"""
    def __init__(cls, class_name, class_parents, class_attrs):
        for attr in class_attrs:
            try:
                if attr == '__doc__':
                    continue
                ret = dis.get_instructions(class_attrs[attr])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.argval == 'connect':
                        raise TypeError('Исползован недопустимый метод "connect"')
        super(ServerVerifier, cls).__init__(class_name, class_parents, class_attrs)
