class ServerError(Exception):
    """Класс обработки ошибок ссоединения с сервером на стороне пользователя"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
