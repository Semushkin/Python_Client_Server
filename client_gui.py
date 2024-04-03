from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QListView, QTextEdit, QPushButton, QDialog, QLineEdit
import sys


class MainWindow(QMainWindow):

     def __init__(self):
         super().__init__()
         self.initUI()

     def initUI(self):

         self.setFixedSize(900, 700)
         self.setWindowTitle('Messenger')

         self.label_contacts = QLabel(self)
         self.label_contacts.setGeometry(20, 10, 100, 20)
         self.label_contacts.setObjectName('label_contacts')
         self.label_contacts.setText('Contacts')

         self.btn_contact_add = QPushButton(self)
         self.btn_contact_add.setGeometry(10, 40, 100, 25)
         self.btn_contact_add.setObjectName('btn_contact_add')
         self.btn_contact_add.setText('Add Contact')

         self.btn_contact_delete = QPushButton(self)
         self.btn_contact_delete.setGeometry(120, 40, 110, 25)
         self.btn_contact_delete.setObjectName('btn_contact_delete')
         self.btn_contact_delete.setText('Delete Contact')

         self.contact_list = QListView(self)
         self.contact_list.setGeometry(10, 80, 200, 600)
         self.contact_list.setObjectName('contact_list')

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

         self.btn_send_message = QPushButton(self)
         self.btn_send_message.setGeometry(240, 650, 90, 25)
         self.btn_send_message.setObjectName('btn_send_message')
         self.btn_send_message.setText('Send')


         self.show()


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
        self.nickname = self.edit_nickname.text()
        self.address = self.edit_address.text()
        self.port = self.edit_port.text()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # main = MainWindow()
    enter = EnterWindow()
    app.exec_()
