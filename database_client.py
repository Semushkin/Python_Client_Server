from datetime import datetime

from sqlalchemy import Column, Integer, String, create_engine, DateTime, or_, Boolean
from sqlalchemy.ext.declarative import declarative_base
from common.variables import DATABASE_CLIENT
from sqlalchemy.orm import sessionmaker
from pprint import pprint


class DataBase:
    Base = declarative_base()

    class Contacts(Base):
        __tablename__ = 'Contacts'
        id = Column(Integer, primary_key=True)
        nickname = Column(String, unique=True)
        unreaded_messages = Column(Boolean, default=False)

        def __init__(self, nickname):
            self.nickname = nickname

        def __str__(self):
            return self.nickname

    class HistoryMessage(Base):
        __tablename__ = 'History'
        id = Column(Integer, primary_key=True)
        sender = Column(String)
        recipient = Column(String)
        message = Column(String)
        date = Column(DateTime)

        def __init__(self, sender, recipient, message):
            self.sender = sender
            self.recipient = recipient
            self.message = message
            self.date = datetime.now()

        def __str__(self):
            return f'from: {self.sender}; to: {self.recipient}; message: {self.message}'

    def __init__(self, client):

        self.engine = create_engine(f'sqlite:///database_client_{client}.db3',
                                    echo=False,
                                    pool_recycle=7200,
                                    connect_args={'check_same_thread': False}
                                    )
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def get_contacts(self):
        """
        :return: list of contacts (nickname, nickname, ...)
        """
        return [[contact.nickname, contact.unreaded_messages] for contact in self.session.query(self.Contacts).all()]

    def check_contact(self, nickname: str):
        """

        :param nickname: nickname of contact
        :return: None
        """
        if self.session.query(self.Contacts).filter_by(nickname=nickname).count():
            return True
        return False

    def add_contact(self, nickname: str) -> None:
        if not self.session.query(self.Contacts).filter_by(nickname=nickname).count():
            new_contact = self.Contacts(nickname)
            self.session.add(new_contact)
            self.session.commit()

    def delete_contact(self, contact):
        self.session.query(self.Contacts).filter_by(nickname=contact).delete()
        self.session.commit()

    def save_history_messages(self, sender: str, recipient: str, message: str) -> None:
        """

        :param sender:  nickname sender
        :param recipient: nickname recipient
        :param message:
        :return: None
        """
        message = self.HistoryMessage(sender, recipient, message)
        self.session.add(message)
        self.session.commit()

    def get_history_messages_by_contact(self, contact) -> list:
        """
        get list of messages

        :param contact: contact
        :return: list
        """
        messages = self.session.query(self.HistoryMessage).filter(or_(
            self.HistoryMessage.sender == contact,
            self.HistoryMessage.recipient == contact
        ))
        return messages

    def new_message_set(self, nickname: str):
        contact = self.session.query(self.Contacts).filter_by(nickname=nickname).first()
        contact.unreaded_messages = True
        self.session.add(contact)
        self.session.commit()

    def new_message_clean(self, nickname: str):
        contact = self.session.query(self.Contacts).filter_by(nickname=nickname).first()
        contact.unreaded_messages = False
        self.session.add(contact)
        self.session.commit()

    def check_new_messages(self, nickname: str):
        """
        :param nickname: str
        :return: Return true if flag "new message" set
        """
        contact = self.session.query(self.Contacts).filter_by(nickname=nickname).first()
        if contact.unreaded_messages:
            return True
        return False


if __name__ == '__main__':
    db_sam = DataBase('Sam')

    db_sam.add_contact('Robert')
    db_sam.add_contact('John')
    db_sam.add_contact('Jack')

    print(db_sam.get_contacts())
    print('---------------------')

    print(db_sam.new_message_set('Robert'))
    print('---------------------')
    print(db_sam.get_contacts())

    # for item in db_sam.get_history_messages_by_contact('Robert'):
    #     print(item)

    # db_sam.delete_contact('Johne')
    # print(db_sam.get_contacts())
    # contacts = [contact[0] for contact in db_sam.get_contacts()]
    # print(contacts)
    # for contact in db_sam.get_contacts():
    #     print(contact)

