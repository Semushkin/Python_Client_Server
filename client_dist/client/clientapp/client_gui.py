from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel,
                             QListView, QTextEdit, QPushButton,
                             QDialog, QLineEdit, QMessageBox,
                             QTableView)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt, pyqtSlot
import sys


class MainWindow(QMainWindow):
    """Класс главного окна пользователя"""
    def __init__(self, database, client):
        super().__init__()
        self.database = database
        self.client = client
        self.initUI()
        self.load_contacts()
        self.connect_signals()
        self.message_window = QMessageBox()
        self.active_chat = None
        self.show()

    def initUI(self):
        self.setFixedSize(900, 700)
        self.setWindowTitle(f'Messenger - {self.client.nickname}')

        self.label_contacts = QLabel(self)
        self.label_contacts.setGeometry(20, 10, 100, 20)
        self.label_contacts.setObjectName('label_contacts')
        self.label_contacts.setText('Contacts')

        self.btn_contact_add = QPushButton('Add Contact', self)
        self.btn_contact_add.setGeometry(10, 40, 100, 25)
        self.btn_contact_add.setObjectName('btn_contact_add')
        self.btn_contact_add.clicked.connect(self.contact_add)

        self.btn_contact_delete = QPushButton('Delete Contact', self)
        self.btn_contact_delete.setGeometry(120, 40, 110, 25)
        self.btn_contact_delete.setObjectName('btn_contact_delete')
        self.btn_contact_delete.clicked.connect(self.contact_delete)

        self.contact_table = QTableView(self)
        self.contact_table.setGeometry(10, 80, 200, 600)
        self.contact_table.setObjectName('contact_table')
        self.contact_table.doubleClicked.connect(self.select_contact)

        self.label_messages = QLabel(self)
        self.label_messages.setGeometry(240, 10, 500, 30)
        self.label_messages.setFont(QFont('Times', 14))
        self.label_messages.setObjectName('label_messages')
        self.label_messages.setText('Messages')

        self.messages_list = QListView(self)
        self.messages_list.setGeometry(240, 40, 640, 440)
        self.messages_list.setObjectName('messages_list')

        self.label_new_message = QLabel(self)
        self.label_new_message.setGeometry(240, 500, 100, 20)
        self.label_new_message.setObjectName('label_new_message')
        self.label_new_message.setText('New message')

        self.text_new_message = QTextEdit(self)
        self.text_new_message.setGeometry(240, 530, 640, 110)
        self.text_new_message.setObjectName('text_new_message')
        self.text_new_message.setEnabled(False)

        self.btn_send_message = QPushButton('Send', self)
        self.btn_send_message.setGeometry(240, 650, 90, 25)
        self.btn_send_message.setObjectName('btn_send_message')
        self.btn_send_message.clicked.connect(self.send_message)

    # Загрузка списка Контактов
    def load_contacts(self):
        """Метод загрузки контактов пользователя из Базы данных"""
        contacts = self.database.get_contacts()
        contacts_model = QStandardItemModel()
        contacts_model.setHorizontalHeaderLabels(['Nickname', ' '])

        for row in range(len(contacts)):
            for column in range(2):
                if column == 1:
                    if contacts[row][column]:
                        item = QStandardItem('new message')
                    else:
                        item = QStandardItem(' ')
                    item.setEnabled(False)
                else:
                    item = QStandardItem(contacts[row][column])
                    item.setEditable(False)
                contacts_model.setItem(row, column, item)
        self.contact_table.setModel(contacts_model)
        self.contact_table.resizeColumnsToContents()

    def contact_add(self):
        """Метод добавления нового контакта пользователя"""
        global add_contact
        add_contact = NewContact(self.database, self.client)
        add_contact.exec()

        self.load_contacts()

    def contact_delete(self):
        """Метод удаления контакта пользователя"""
        contact = self.contact_table.currentIndex().data()
        if contact:
            if self.message_window.question(self,
                                            'Удаление контакта',
                                            f'Удалить контакт "{contact}" ?',
                                            QMessageBox.Yes,
                                            QMessageBox.No
                                            ) == QMessageBox.Yes:
                self.client.delete_contact(contact)
                self.load_contacts()

    def select_contact(self):
        """Метод выбора контакта пользователя для открытия чата с ним"""
        self.active_chat = self.contact_table.currentIndex().data()
        self.label_messages.setText(f'Чат с пользователем - {self.active_chat}')
        self.load_messages_list()

    # Загрузка истории сообщений с выбранным контактом
    def load_messages_list(self):
        """Метод загрузки истории сообщений с контактом"""
        if self.active_chat:
            self.text_new_message.setEnabled(True)
        else:
            self.text_new_message.setEnabled(False)
            return False
        messages = self.database.get_history_messages_by_contact(self.active_chat)
        history_messages_model = QStandardItemModel()
        for message in messages:
            item = QStandardItem(f'from {message.sender}, '
                                 f'to {message.recipient}, '
                                 f'date {message.date}\n {message.message}')
            if message.sender == self.client.nickname:
                item.setTextAlignment(Qt.AlignRight)
            item.setEditable(False)
            history_messages_model.appendRow(item)
        self.database.new_message_clean(self.active_chat)
        self.load_contacts()
        self.messages_list.setModel(history_messages_model)
        self.messages_list.scrollToBottom()

    def send_message(self):
        """Метод отправкии сообщения контакту"""
        message = self.text_new_message.toPlainText()
        if message:
            self.text_new_message.clear()
            contact = self.active_chat
            self.client.send_message(message, contact)
            self.load_messages_list()

    @pyqtSlot(str)
    def receive_message(self, contact):
        """Метод получения сообщений"""
        if not self.active_chat == contact and not self.database.check_new_messages(contact):
            self.database.new_message_set(contact)
            self.load_contacts()
            self.message_window.information(self, 'Новое сообщение', f'Получено новое сообщение от {contact}')
        else:
            self.load_messages_list()

    @pyqtSlot()
    def connection_lost(self):
        """Метод закрытия приложения пользователя при потере соединения с сервером."""
        self.message_window.critical(self, 'Ошибка!!!', 'Потеряно соединение!')
        self.close()

    @pyqtSlot(str)
    def new_contact(self, nickname: str) -> None:
        """Метод добавление нового контакта пользователя по средствам слота pyqtSlot. Сигнал генерируется emit() """
        self.client.add_contact(nickname)
        self.load_contacts()

    def connect_signals(self):
        """Метод подключения слотов pyqtSlot. Для отлавливания сгенерированных emit() сигналов"""
        self.client.signal_new_message.connect(self.receive_message)
        self.client.connection_lost.connect(self.connection_lost)
        self.client.signal_new_contact.connect(self.new_contact)


class EnterWindow(QDialog):
    """Класс окна входа (логин, пароль) в приложение пользователя"""
    def __init__(self):
        super().__init__()
        self.nickname = ''
        self.password = ''

        self.setFixedSize(270, 220)
        self.setWindowTitle('Login')

        self.lable_comment = QLabel('Nickname - обязательно\nip и port не обязательно', self)
        self.lable_comment.setGeometry(10, 10, 200, 40)

        self.label_nickname = QLabel('Nickname', self)
        self.label_nickname.setGeometry(20, 50, 70, 20)

        self.edit_nickname = QLineEdit(self)
        self.edit_nickname.setGeometry(100, 50, 120, 25)

        self.label_password = QLabel('Password', self)
        self.label_password.setGeometry(20, 90, 70, 20)

        self.edit_password = QLineEdit(self)
        self.edit_password.setGeometry(100, 90, 120, 25)

        self.btn_enter = QPushButton('Login', self)
        self.btn_enter.setGeometry(20, 180, 90, 25)
        self.btn_enter.clicked.connect(self.enter)

        self.btn_exit = QPushButton('Exit', self)
        self.btn_exit.setGeometry(150, 180, 90, 25)
        self.btn_exit.clicked.connect(self.close)

        self.show()

    def enter(self):
        """Метод проверки корректности ввода логина пользователя"""
        if not self.edit_nickname.text():
            message = QMessageBox()
            message.warning(self, 'Ошибка!!!', 'Не верное имя пользователя')
        else:
            self.nickname = self.edit_nickname.text()
            self.password = self.edit_password.text()
            self.close()


class NewContact(QDialog):
    """Класс окна добавления нового контакта пользователя"""
    def __init__(self, database, client):
        super().__init__()
        self.database = database
        self.client = client
        self.initUI()
        self.show()

    def initUI(self):

        self.setFixedSize(270, 220)
        self.setWindowTitle('New Contact')

        self.label_nickname = QLabel('Nickname', self)
        self.label_nickname.setGeometry(20, 50, 70, 20)

        self.edit_nickname = QLineEdit(self)
        self.edit_nickname.setGeometry(100, 50, 120, 25)

        self.btn_add_contact = QPushButton('Add', self)
        self.btn_add_contact.setGeometry(20, 180, 90, 25)
        self.btn_add_contact.clicked.connect(self.add_contact)

        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setGeometry(150, 180, 90, 25)
        self.btn_cancel.clicked.connect(self.close)

    def add_contact(self):
        """Метод добавления нового контакта пользователя"""
        message = QMessageBox()
        if self.client.add_contact(self.edit_nickname.text()):
            message.information(self, 'Новый Контакт', 'Добавлено')
            self.close()
            # Контакт успешно добавлен
        else:
            message.warning(self, 'Новый контакт', 'Данный контакт незарегистрирован')
            self.close()
            # Ошибка добавления контакта


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    app.exec_()
