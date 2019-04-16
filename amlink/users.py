from sqlalchemy import Column, Integer, Text

from amlink.database_controller import Base, initSession, createTables, checkDatabase

session = initSession()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text, nullable=False, unique=True, index=True)
    password = Column(Text, nullable=False, index=True)

    @classmethod
    def getByName(cls, name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def getById(cls, id):
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def delete(cls, user):
        session.delete(user)

    @classmethod
    def add(cls, name, pwd):
        user = cls(name=name, password=pwd)
        session.add(user)
        session.commit()

    def checkPassword(self, psd):
        return self.password == psd


def initdb():
    if not checkDatabase(Users)[0]:
        createTables()


def closedb():
    session.close()


def user_look_up(name_entity_data, user):
    pass


def get_user(name):
    return Users.getByName(name)


def create_user(name, pwd):
    Users.add(name, pwd)


def del_user(name):
    Users.delete(name)
