from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QTableView, QApplication, QDialog, QPushButton, \
    QLineEdit, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import sys


# def create_model(database):
#     list_users = database.active_users_list()
#     list = QStandardItemModel()
#     list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
#     for row in list_users:
#         user, ip, port, time = row
#         user = QStandardItem(user)
#         user.setEditable(False)
#         ip = QStandardItem(ip)
#         ip.setEditable(False)
#         port = QStandardItem(str(port))
#         port.setEditable(False)
#         # Уберём милисекунды из строки времени, т.к. такая точность не требуется.
#         time = QStandardItem(str(time.replace(microsecond=0)))
#         time.setEditable(False)
#         list.appendRow([user, ip, port, time])
#     return list


def create_connections_model(database):
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
    history_list = database.get_history()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Клиент', 'Дата входа','IP адрес'])
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
    clients = database.get_all_client()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Клиент'])
    for client in clients:
        client = QStandardItem(client)
        client.setEditable(False)
        model.appendRow([client])
    return model

class MainWindow(QMainWindow):

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
        self.setWindowTitle('Messenger')

        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 35)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 55)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()


class HistoryWindow(QDialog):
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
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Список зарегистрированных клиентов')
        self.setFixedSize(350, 470)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 440)
        self.close_button.clicked.connect(self.close)

        self.client_table = QTableView(self)
        self.client_table.move(10, 10)
        self.client_table.setFixedSize(300, 420)

        self.show()

class ConfigWindow(QDialog):
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
            #path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150 , 20)

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

        self.save_btn = QPushButton('Сохранить' , self)
        self.save_btn.move(190 , 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    app.exec_()
