from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel, QListView, QTextEdit, QPushButton, QDialog, QLineEdit,
                             QMessageBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSlot
import sys


class MainWindow(QMainWindow):

    def __init__(self, database, client):
         super().__init__()
         self.btn_send_message = None
         self.database = database
         self.client = client
         self.initUI()
         self.load_contacts()
         self.connect_signals()
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

        self.contact_list = QListView(self)
        self.contact_list.setGeometry(10, 80, 200, 600)
        self.contact_list.setObjectName('contact_list')
        self.contact_list.doubleClicked.connect(self.load_messages_list)

        self.label_messages = QLabel(self)
        self.label_messages.setGeometry(240, 10, 100, 20)
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

        self.btn_send_message = QPushButton('Send', self)
        self.btn_send_message.setGeometry(240, 650, 90, 25)
        self.btn_send_message.setObjectName('btn_send_message')
        self.btn_send_message.clicked.connect(self.send_message)

    # Загрузка списка Контактов
    def load_contacts(self):
        contacts = self.database.get_contacts()
        contacts_model = QStandardItemModel()
        for contact in contacts:
            item = QStandardItem(contact)
            item.setEditable(False)
            contacts_model.appendRow(item)
        self.contact_list.setModel(contacts_model)

    def contact_add(self):
        global add_contact
        add_contact = NewContact(self.database, self.client)
        add_contact.exec()

        self.load_contacts()

    def contact_delete(self):
        data = self.contact_list.currentIndex().data()
        if data:
            info = QMessageBox()
            info.setWindowTitle('Удаление контакта')
            info.setText(f'Удалить контакт "{data}" ?')
            info.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            button = info.exec()
            if button == QMessageBox.Yes:
                self.client.delete_contact(data)
                self.load_contacts()

    # Загрузка истории сообщений с выбранным контактом
    def load_messages_list(self):
        current_contact = self.contact_list.currentIndex().data()
        messages = self.database.get_history_messages_by_contact(current_contact)
        history_messages_model = QStandardItemModel()
        for message in messages:
            item = QStandardItem(f'from {message.sender}, to {message.recipient}, date {message.date}\n {message.message}')
            if message.sender == self.client.nickname:
                item.setTextAlignment(Qt.AlignRight)
            item.setEditable(False)
            history_messages_model.appendRow(item)
        self.messages_list.setModel(history_messages_model)
        self.messages_list.scrollToBottom()

    def send_message(self):
        message = self.text_new_message.toPlainText()
        self.text_new_message.clear()
        contact = self.contact_list.currentIndex().data()
        if message:
            self.client.send_message(message, contact)
            print('Сообщение отправлено!')
            self.load_messages_list()

    @pyqtSlot(str)
    def receive_message(self):
        self.load_messages_list()

    def connect_signals(self):
        self.client.signal_new_message.connect(self.receive_message)


class EnterWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.nickname = ''
        self.address = ''
        self.port = ''

        self.setFixedSize(270, 220)
        self.setWindowTitle('Login')

        self.lable_comment = QLabel('Nickname - обязательно\nip и port не обязательно', self)
        self.lable_comment.setGeometry(10, 10, 200, 40)

        self.label_nickname = QLabel('Nickname', self)
        self.label_nickname.setGeometry(20, 50, 70, 20)

        self.edit_nickname = QLineEdit(self)
        self.edit_nickname.setGeometry(100, 50, 120, 25)

        self.label_address = QLabel('IP Address', self)
        self.label_address.setGeometry(20, 90, 70, 20)

        self.edit_address = QLineEdit(self)
        self.edit_address.setGeometry(100, 90, 120, 25)

        self.label_port = QLabel('Port', self)
        self.label_port.setGeometry(20, 130, 70, 20)

        self.edit_port = QLineEdit(self)
        self.edit_port.setGeometry(100, 130, 120, 25)

        self.btn_enter = QPushButton('Login', self)
        self.btn_enter.setGeometry(20, 180, 90, 25)
        self.btn_enter.clicked.connect(self.enter)

        self.btn_exit = QPushButton('Exit', self)
        self.btn_exit.setGeometry(150, 180, 90, 25)
        self.btn_exit.clicked.connect(self.close)

        self.show()

    def enter(self):
        if not self.edit_nickname.text():
            message = QMessageBox()
            message.warning(self, 'Ошибка!!!' ,'Не верное имя пользователя')
        else:
            self.nickname = self.edit_nickname.text()
            self.address = self.edit_address.text()
            self.port = self.edit_port.text()
            self.close()


class NewContact(QDialog):
    def __init__(self, database=None, client=None):
        super().__init__()
        self.database = database
        self.client = client
        self.initUI()
        self.show()

    def initUI(self):

        self.setFixedSize(270, 220)
        self.setWindowTitle('New Contact')

        self.label_nickname = QLabel('Nickname', self)
        self.label_nickname.setGeometry(20, 50 ,70, 20)

        self.edit_nickname = QLineEdit(self)
        self.edit_nickname.setGeometry(100, 50, 120, 25)

        self.btn_add_contact = QPushButton('Add', self)
        self.btn_add_contact.setGeometry(20, 180, 90, 25)
        self.btn_add_contact.clicked.connect(self.add_contact)

        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setGeometry(150, 180, 90, 25)
        self.btn_cancel.clicked.connect(self.close)

    def add_contact(self):
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
    # main = MainWindow()
    # enter = EnterWindow()
    add_contact = NewContact()
    app.exec_()
