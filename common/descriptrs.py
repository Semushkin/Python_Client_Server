class Port:
    """Класс проверки корректности введенного номера IP порта"""
    def __set__(self, instance, value):
        if value < 1025:
            print('Ошибка!!! Порт не может быть меньше 1025')
            exit(1)
        if value > 65536:
            print('Ошибка!!! Порт не может быть больше 65536')
            exit(1)
        instance.__dict__[self.my_attr] = value

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr
