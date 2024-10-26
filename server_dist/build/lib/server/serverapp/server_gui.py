import sys
from hashlib import pbkdf2_hmac
from binascii import hexlify

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QTableView, QApplication, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem


def create_connections_model(database):
    """Метод создания GUI модели таблицы подключившехся клиентов"""
    conn_list = database.get_active_list()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Клиент', 'IP адрес'])
    for row in conn_list:
        client, ip = row
        client = QStandardItem(client)
        client.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        model.appendRow([client, ip])
    return model


def create_stat_model(database):
    """Метод создания GUI модели таблицы истории подключений клиентов"""
    history_list = database.get_history()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Клиент', 'IP адрес', 'Дата входа'])
    for row in history_list:
        client, date, ip = row
        client = QStandardItem(client)
        client.setEditable(False)
        date = QStandardItem(date)
        date.setEditable(False)
        ip = QStandardItem(str(ip))
        ip.setEditable(False)
        model.appendRow([client, date, ip])
    return model


def create_clients_list(database):
    """Метод создания GUI модели таблицы всех клиентов"""
    clients = database.get_all_client()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Клиент'])
    for client in clients:
        client = QStandardItem(client)
        client.setEditable(False)
        model.appendRow([client])
    return model


class MainWindow(QMainWindow):
    """Класс главного окна GUI приложения Сервера"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Обновить список', self)
        self.config_btn = QAction('Настройки сервера', self)
        self.client_btn = QAction('Список клиентов', self)
        self.show_history_button = QAction('История клиентов', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exit_action)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.client_btn)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)

        self.setFixedSize(800, 500)
        self.setWindowTitle('Server')

        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 35)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 55)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()


class HistoryWindow(QDialog):
    """Класс окна отоброжения списка истории подключения клиентов"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()


class ClientsWindow(QDialog):
    """Класс отображения окна всех зарегестрированных клиентов, с возможностью их добавления и удаления."""
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.message = QMessageBox()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Список зарегистрированных клиентов')
        self.setFixedSize(350, 470)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.btn_add_client = QPushButton('Добавить', self)
        self.btn_add_client.move(10, 440)
        self.btn_add_client.clicked.connect(self.add_client)

        self.btn_delete_client = QPushButton('Удалить', self)
        self.btn_delete_client.move(100, 440)
        self.btn_delete_client.clicked.connect(self.delete_client)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 440)
        self.close_button.clicked.connect(self.close)

        self.client_table = QTableView(self)
        self.client_table.move(10, 10)
        self.client_table.setFixedSize(300, 420)

        self.show()

    def add_client(self):
        """Метод добавления нового ползователя"""
        global add_new_client
        add_new_client = AddClient(self.database)
        # add_new_client.show()
        add_new_client.exec_()
        self.update_table()
        # self.message.information(self, 'rrrrrrrrrrrr rrrrrrrrrrrr', 'rrrrrrrrrrrr')

    def delete_client(self):
        """Метод удаления ползователя"""
        client = self.client_table.currentIndex().data()

        if client:
            if self.message.question(
                    self,
                    'Удаление клиента',
                    f'Удалить контакт "{client}" ?',
                    QMessageBox.Yes,
                    QMessageBox.No
            ) == QMessageBox.Yes:
                self.database.delete_client(client)
                self.update_table()

    def update_table(self):
        """Метод обновления в окне списка зарегистрированных пользователей, после операции добавления или удаления"""
        self.client_table.setModel(create_clients_list(self.database))
        self.client_table.resizeColumnsToContents()
        self.client_table.resizeRowsToContents()


class ConfigWindow(QDialog):
    """Класс окна настроек"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            # path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(' оставьте это поле пустым, чтобы\n принимать соединения с любых адресов.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


class AddClient(QDialog):
    """Класс окна добавления нового пользовтеля"""
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.initUI()

    def initUI(self):

        self.message = QMessageBox()

        self.setWindowTitle('Добавление нового клиента')
        self.setFixedSize(350, 200)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 440)
        self.close_button.clicked.connect(self.close)

        self.label_nickname = QLabel('Nickname', self)
        self.label_nickname.setGeometry(20, 50, 100, 20)

        self.edit_nickname = QLineEdit(self)
        self.edit_nickname.setGeometry(130, 50, 160, 25)

        self.label_password_1 = QLabel('Password', self)
        self.label_password_1.setGeometry(20, 90, 100, 20)

        self.edit_password_1 = QLineEdit(self)
        self.edit_password_1.setGeometry(130, 90, 160, 25)

        self.label_password_2 = QLabel('Password (Repeat)', self)
        self.label_password_2.setGeometry(20, 130, 100, 20)

        self.edit_password_2 = QLineEdit(self)
        self.edit_password_2.setGeometry(130, 130, 160, 25)

        self.btn_save = QPushButton('Сохранить', self)
        self.btn_save.setGeometry(20, 170, 100, 20)
        self.btn_save.clicked.connect(self.save)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setGeometry(200, 170, 100, 20)
        self.btn_cancel.clicked.connect(self.close)

        self.show()

    def save(self):
        """Метод сохранения данных нового пользователя, с предваретельной проверкой корректности указанных данных"""
        if not self.edit_nickname.text() or not self.edit_password_1.text() or not self.edit_password_2.text():
            self.message.critical(self, 'Ошибка!!!', 'Ошибка! Форма не заполнена')
            # self.close()
        else:
            if self.database.get_client_by_name(self.edit_nickname.text()):
                self.message.critical(self, 'Ошибка!!!', 'Ошибка! Данный пользователь уже заергистрирован.')
            elif self.edit_password_1.text() != self.edit_password_2.text():
                self.message.critical(self, 'Ошибка!!!', 'Ошибка! Пароли не совпадают')
            else:
                passwd = self.edit_password_1.text().encode('utf-8')
                salt = self.edit_nickname.text().lower().encode('utf-8')
                passwd = pbkdf2_hmac('sha512', passwd, salt, 10000)

                self.database.add_client(self.edit_nickname.text(), hexlify(passwd))

                self.message.information(self, 'Добавление пользователя', 'Добавлено!')
                self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    app.exec_()
