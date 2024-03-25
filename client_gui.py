from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QListView
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

         self.contact_list = QListView(self)
         self.contact_list.setGeometry(10, 40, 200, 600)
         self.contact_list.setObjectName('contact_list')

         self.contact_list = QListView(self)
         self.contact_list.setGeometry(10, 40, 200, 600)
         self.contact_list.setObjectName('messages_list')

         self.contact_list = QListView(self)
         self.contact_list.setGeometry(10, 40, 200, 600)
         self.contact_list.setObjectName('new_message')

         self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    app.exec_()
