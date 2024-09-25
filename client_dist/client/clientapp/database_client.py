from datetime import datetime

from sqlalchemy import Column, Integer, String, create_engine, DateTime, or_, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DataBase:
    """Класс работы с базой данных на стороне Пользователя на базе SQLite3 и SQLAlchemy"""
    Base = declarative_base()
    """Ghfjkfg"""

    class Contacts(Base):
        """Класс отображения Контактов Пользователя"""
        __tablename__ = 'Contacts'
        id = Column(Integer, primary_key=True)
        nickname = Column(String, unique=True)
        unreaded_messages = Column(Boolean, default=False)

        def __init__(self, nickname):
            self.nickname = nickname

        def __str__(self):
            return self.nickname

    class HistoryMessage(Base):
        """Класс отображения истории переписки Пользователя"""
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
        """Метод получения контактов Пользователя"""
        return [[contact.nickname, contact.unreaded_messages] for contact in self.session.query(self.Contacts).all()]

    def check_contact(self, nickname: str):
        """Метод проверки наличия пользователя в базе сервера"""
        if self.session.query(self.Contacts).filter_by(nickname=nickname).count():
            return True
        return False

    def add_contact(self, nickname: str) -> None:
        """Метод добавления контакта пользователя в базу данных"""
        if not self.session.query(self.Contacts).filter_by(nickname=nickname).count():
            new_contact = self.Contacts(nickname)
            self.session.add(new_contact)
            self.session.commit()

    def delete_contact(self, contact):
        """Метод удаления контакта пользователя из базы"""
        self.session.query(self.Contacts).filter_by(nickname=contact).delete()
        self.session.commit()

    def save_history_messages(self, sender: str, recipient: str, message: str) -> None:
        """Метод сохранения сообщения в истории переписок"""
        message = self.HistoryMessage(sender, recipient, message)
        self.session.add(message)
        self.session.commit()

    def get_history_messages_by_contact(self, contact) -> list:
        """Метод получения списка сообщений пользователя с определенным контактом"""
        messages = self.session.query(self.HistoryMessage).filter(or_(
            self.HistoryMessage.sender == contact,
            self.HistoryMessage.recipient == contact
        ))
        return messages

    def new_message_set(self, nickname: str):
        """Метод записи в базе о наличие нового не прочитанного сообщения от контакта пользователя"""
        contact = self.session.query(self.Contacts).filter_by(nickname=nickname).first()
        contact.unreaded_messages = True
        self.session.add(contact)
        self.session.commit()

    def new_message_clean(self, nickname: str):
        """Метод снятия отметки о наличие нового не прочитанного сообщения от контакта пользователя"""
        contact = self.session.query(self.Contacts).filter_by(nickname=nickname).first()
        contact.unreaded_messages = False
        self.session.add(contact)
        self.session.commit()

    def check_new_messages(self, nickname: str):
        """Метод проверки наличия отметки о """
        contact = self.session.query(self.Contacts).filter_by(nickname=nickname).first()
        if contact.unreaded_messages:
            return True
        return False


if __name__ == '__main__':
    pass
