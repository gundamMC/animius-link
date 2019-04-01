from sqlalchemy import Column, String, Integer, Boolean, create_engine, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship,session as s,scoped_session
from database_controller import Base,initSession,closeSession
import time

session = initSession()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text,nullable=False,unique=True,index=True)
    password = Column(Text,nullable=False,index=True)
    notes = relationship("Notes", backref='user', lazy='dynamic')
    notes_category = relationship("NotesCategory", backref='user', lazy='dynamic')
    reminders = relationship("Reminders", backref='user', lazy='dynamic')
    reminders_category = relationship("RemindersCategory", backref='user', lazy='dynamic')

    @classmethod
    def getByName(cls,name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def getById(cls,id):
        return session.query(cls).filter_by(id=id).first()

    def checkPassword(self,psd):
        return self.password == psd
