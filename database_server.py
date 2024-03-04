from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from common.variables import DATABASE

class DataBase:
    Base = declarative_base()

    class Clients(Base):
        __tablename__ = 'Clients'
        id = Column(Integer, primary_key=True)
        nickname = Column(String, unique=True)

        def __init__(self, nickname):
            self.nickname = nickname

        # def __str__(self):
        #     return self.nickname

    class History(Base):
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
        __tablename__ = 'ActiveClients'
        id = Column(Integer, primary_key=True)
        client_id = Column(String, ForeignKey('Clients.id'), unique=True)
        ip = Column(String)

        def __init__(self, client_id, ip):
            self.client_id = client_id
            self.ip = ip

        def __str__(self):
            return f'Клиент {self.client_id}, ip {self.ip}'

    def __init__(self):

        self.engine = create_engine(DATABASE, echo=False, pool_recycle=7200)
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.ActiveClients).delete()
        self.session.commit()

    def client_entry(self, nickname, ip):
        client = self.session.query(self.Clients).filter_by(nickname=nickname)
        if not client.count():
            client = self.Clients(nickname=nickname)
            self.session.add(client)
            self.session.commit()
        else:
            client = client.first()

        active = self.ActiveClients(client.id, ip)
        history = self.History(client.id, datetime.now(), ip)
        self.session.add(active)
        self.session.add(history)
        self.session.commit()


    def client_exit(self, nickname):
        client = self.session.query(self.Clients).filter_by(nickname=nickname).first()
        self.session.query(self.ActiveClients).filter_by(client_id=client.id).delete()
        self.session.commit()

    def get_active_list(self):
        result = self.session.query(self.Clients.nickname, self.ActiveClients.ip).join(self.Clients)
        return result.all()


    def get_history(self):
        result = self.session.query(self.Clients.nickname, self.History.ip, self.History.date_entry).join(self.Clients)
        return result.all()

if __name__ == '__main__':
    db  = DataBase()
    # db.client_entry('John','127.0.0.1')
    # db.client_entry('Sam', '127.0.0.1')
    # db.client_entry('Robert', '127.0.0.1')
    print('----------------------------------------------------------------')
    print('-------------------Пользователи онлайн--------------------------')
    client_online = db.get_active_list()
    if client_online:
        for item in client_online:
            print(f'Клиент: {item[0]}; с адресом ip: {item[1]}')
    else:
        print('Нет подключенных пользователей')
    print('----------------------------------------------------------------')
    print('-------------------------История--------------------------------')
    client_history = db.get_history()
    if client_history:
        for item in client_history:
            print(f'Клиент: {item[0]}; с адресом ip: {item[1]}; вход: {item[2]}')
    else:
        print('Нет истории подключений')
    print('----------------------------------------------------------------')

    db.client_entry('Robert', '127.0.0.1')