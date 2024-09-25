from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from common.variables import DATABASE_SERVER


class DataBase:
    """Класс работы с базой данных на стороне Сервера на базе SQLite3 и SQLAlchemy"""
    Base = declarative_base()

    class Clients(Base):
        """Класс отображения Клиентов"""
        __tablename__ = 'Clients'
        id = Column(Integer, primary_key=True)
        nickname = Column(String, unique=True)
        password_hash = Column(String, unique=True)
        public_key = Column(Text)

        def __init__(self, nickname, password):
            self.nickname = nickname
            self.password_hash = password

        def __str__(self):
            return self.nickname

    class History(Base):
        """Класс отображения истории подлючавшихся Клиентов"""
        __tablename__ = 'History'
        id = Column(Integer, primary_key=True)
        client_id = Column(String, ForeignKey('Clients.id'))
        date_entry = Column(DateTime)
        ip = Column(String)

        def __init__(self, client_id, date_entry, ip):
            self.client_id = client_id
            self.date_entry = date_entry
            self.ip = ip

        def __str__(self):
            return f'Клиент {self.client_id}, ip {self.ip}, последний вход {self.date_entry}'

    class ActiveClients(Base):
        """Класс отображения активных(подключенных) Клиентов"""
        __tablename__ = 'ActiveClients'
        id = Column(Integer, primary_key=True)
        client_id = Column(String, ForeignKey('Clients.id'), unique=True)
        ip = Column(String)

        def __init__(self, client_id, ip):
            self.client_id = client_id
            self.ip = ip

        def __str__(self):
            return f'Клиент {self.client_id}, ip {self.ip}'

    class Contacts(Base):
        """Класс отображения контактов Клиента"""
        __tablename__ = 'Contacts'
        id = Column(Integer, primary_key=True)
        client_id = Column(String, ForeignKey('Clients.id'))
        contact_id = Column(String, ForeignKey('Clients.id'))

        def __init__(self, client_id, contact_id):
            self.client_id = client_id
            self.contact_id = contact_id

    def __init__(self):

        self.engine = create_engine(
            DATABASE_SERVER,
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.ActiveClients).delete()
        self.session.commit()

    def get_client_by_name(self, nickname):
        """Метод получения клиента по имени"""
        return self.session.query(self.Clients).filter_by(nickname=nickname).first()

    def add_client(self, nickname, passwd):
        """Метод добавления нового клиента"""
        client = self.Clients(nickname, passwd)
        self.session.add(client)
        self.session.commit()

    def delete_client(self, nickname):
        """Метод удаления клиента"""
        self.session.query(self.Clients).filter_by(nickname=nickname).delete()
        self.session.commit()

    def client_entry(self, nickname, ip):
        """Метод добавления клиента в список активных(подключившехся) клиентов и добавление записи в историю входов"""
        client = self.session.query(self.Clients).filter_by(nickname=nickname).first()

        active = self.ActiveClients(client.id, ip)
        history = self.History(client.id, datetime.now(), ip)
        self.session.add(active)
        self.session.add(history)
        self.session.commit()

    def client_exit(self, nickname):
        """Метод удаления клиента из списка активных пользователей"""
        client = self.session.query(self.Clients).filter_by(nickname=nickname).first()
        self.session.query(self.ActiveClients).filter_by(client_id=client.id).delete()
        self.session.commit()

    def get_active_list(self):
        """Метод получения списка активных пользователей"""
        result = self.session.query(self.Clients.nickname, self.ActiveClients.ip).join(self.Clients)
        return result.all()

    def get_history(self):
        """Метод получения истории подключений клиентов"""
        result = self.session.query(self.Clients.nickname, self.History.ip, self.History.date_entry).join(self.Clients)
        return result.all()

    def get_contacts(self, nickname):
        """Метод получения списка контактов пользователя"""
        client = self.session.query(self.Clients).filter_by(nickname=nickname).first()
        query = self.session.query(self.Contacts, self.Clients.nickname).filter_by(client_id=client.id).join(self.Clients, self.Contacts.contact_id == self.Clients.id)
        return [item[1] for item in query.all()]

    def add_contact(self, client_name, contact):
        """Метод добавления нового контакта клиента"""
        client = self.session.query(self.Clients).filter_by(nickname=client_name).first()
        contact = self.session.query(self.Clients).filter_by(nickname=contact).first()

        if not contact:
            return False

        if self.session.query(self.Contacts).filter_by(client_id=client.id, contact_id=contact.id).count():
            return True

        new_contact = self.Contacts(client.id, contact.id)
        self.session.add(new_contact)
        self.session.commit()
        return True

    def delete_contact(self, client_name, contact):
        """Метод уаления контакта из списка контактов клиента"""
        client = self.session.query(self.Clients).filter_by(nickname=client_name).first()
        contact = self.session.query(self.Clients).filter_by(nickname=contact).first()

        if not contact:
            return False

        del_contact = self.session.query(self.Contacts).filter(self.Contacts.client_id == client.id,
                                                               self.Contacts.contact_id == contact.id)
        del_contact.delete()
        self.session.commit()
        return True

    def get_all_client(self):
        """Метод получения списка всех известных клиентов"""
        return [client[0] for client in self.session.query(self.Clients.nickname).all()]

    def get_all_contacts(self):
        """Метод получения списка всех контаков"""
        return self.session.query(self.Contacts).join(self.Clients)

    def check_client(self, nickname):
        """Метод проверки наличия клиента с списке зарегистрированных"""
        if self.session.query(self.Clients).filter_by(nickname=nickname).count():
            return True
        return False


if __name__ == '__main__':
    pass
