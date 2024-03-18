from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from common.variables import DATABASE_CLIENT
from sqlalchemy.orm import sessionmaker

class DataBase:
    Base = declarative_base()

    class Contacts(Base):
        __tablename__ = 'Contacts'
        id = Column(Integer, primary_key=True)
        nickname = Column(String, unique=True)

        def __init__(self, nickname):
            self.nickname = nickname

        def __str__(self):
            return self.nickname

    class History(Base):
        __tablename__ = 'History'
        id = Column(Integer, primary_key=True)
        form_user = Column(String)
        to_user = Column(String)
        message = Column(String)
        date = Column(DateTime)


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
        return [contact[0] for contact in self.session.query(self.Contacts.nickname).all()]

    def add_contact(self, contact):
        if not self.session.query(self.Contacts).filter_by(nickname=contact).count():
            new_contact = self.Contacts(contact)
            self.session.add(new_contact)
            self.session.commit()

    def delete_contact(self, contact):
        self.session.query(self.Contacts).filter_by(nickname=contact).delete()


if __name__ == '__main__':
    db_sam = DataBase('Sam')

    db_sam.add_contact('Robert')
    db_sam.add_contact('John')
    db_sam.add_contact('Jack')

    print(db_sam.get_contacts())

    # db_sam.delete_contact('Johne')
    # print(db_sam.get_contacts())
    # contacts = [contact[0] for contact in db_sam.get_contacts()]
    # print(contacts)
    # for contact in db_sam.get_contacts():
    #     print(contact)

