from sqlalchemy import Column, String, Integer, Boolean, create_engine, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship,session as s
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ProgrammingError
import time,sqlalchemy

Base = declarative_base()
conn = "sqlite:///Animius_Link.db"
# init connection
engine = create_engine(conn)
# create sessionmaker:
DBSession = sessionmaker(bind=engine)
session = None # type:s.Session

def checkDatabase():
    try:
        engine = create_engine(conn)
        DBSession = sessionmaker(bind=engine)
        dbs = DBSession()
        dbs.query(Notes).first()
        dbs.query(NotesCategory).first()
        return (True,0,"")
    except ProgrammingError as err:
        return (False,err.code,err.orig)

def initSession():
    # init connection
    engine = create_engine(conn)
    # create sessionmaker:
    DBSession = sessionmaker(bind=engine)

    return DBSession, engine


def createTables():
    try:
        engine = create_engine(conn)
        sessionmaker(bind=engine)().execute("PRAGMA foreign_keys = ON")
        Base.metadata.create_all(engine)
        return True
    except:
        return False


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text,nullable=False,unique=True,index=True)
    password = Column(Text,nullable=False,index=True)
    notes = relationship("Notes", backref='user', lazy='dynamic')
    notes_category = relationship("NotesCategory", backref='user', lazy='dynamic')

    @classmethod
    def getByName(cls,name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def getById(cls,id):
        return session.query(cls).filter_by(id=id).first()

    def checkPassword(self,psd):
        return self.password == psd



class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(Text,index=True)
    note = Column(Text)
    time = Column(Integer)
    category_id = Column(Integer,ForeignKey("note_category.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    @classmethod
    def getLatest(cls,user,num=1):
        """
        :param user: User object
        :param num:
        :return:
        """
        return session.query(cls).filter_by(user_id = user.id).order_by(Notes.title.desc()).limit(num).all()

    @classmethod
    def getAll(cls,user):
        """
        :param user: User object
        :return:
        """
        return session.query(Notes).filter_by(user_id=user.id).all()

    @classmethod
    def seachByTitle(cls,user,title):
        """
        :param user: User object
        :param title:
        :return:
        """
        return session.query(Notes).filter_by(user_id = user.id,title=title).all()

    @classmethod
    def add(cls,user,title,note,category):
        note0 = cls(title=title,note=note,time = int(time.time()),category_id=category.id,user_id=user.id)
        session.add(note0)
        session.commit()
        return True



class NotesCategory(Base):
    __tablename__ = 'note_category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = relationship("Notes", backref='category', lazy='dynamic')


    @classmethod
    def getByName(cls,user,name):
        return session.query(NotesCategory).filter_by(user_id=user.id,name=name).first()

    @classmethod
    def getNotesByName(cls,user,name):
        cate = cls.getByName(user,name) # type: NotesCategory
        if cate == None:
            return []
        return cate.notes

    @classmethod
    def getNotesById(cls,user,id):
        return session.query(NotesCategory).filter_by(user_id=user.id,id=id).first()

    @classmethod
    def add(cls,user,name):
        cate = cls.getByName(user,name)
        if cate != None:
            return False
        cate = cls(user_id=user.id,name=name)
        session.add(cate)
        session.commit()
        return True

