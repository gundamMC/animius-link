from sqlalchemy import Column, String, Integer, Boolean, create_engine, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ProgrammingError
import time

Base = declarative_base()
conn = "sqlite:///Animius_Link.db"
# init connection
engine = create_engine(conn)
# create sessionmaker:
DBSession = sessionmaker(bind=engine)
session = None

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


class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(Text,index=True)
    note = Column(Text)
    time = Column(Integer)
    category_id = Column(Integer,ForeignKey("note_category.id"))

    @classmethod
    def getLatest(cls,num=1):
        return session.query(cls).order_by(Notes.title.desc()).limit(num).all()

    @classmethod
    def getAll(cls):
        return session.query(Notes).all()

    @classmethod
    def seachByTitle(cls,title):
        return session.query(Notes).filter_by(title=title).all()

    @classmethod
    def add(cls, title,note,category_id):
        note0 = cls(title=title,note=note,time = int(time.time()),category_id=category_id)
        session.add(note0)
        session.commit()
        return True



class NotesCategory(Base):
    __tablename__ = 'note_category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text, index=True,unique=True)
    notes = relationship("Notes", backref='category', lazy='dynamic')

    @classmethod
    def getByName(cls,name):
        return session.query(NotesCategory).filter_by(name=name).first()

    @classmethod
    def getNotesByName(cls,name):
        cate = cls.getByName(name) # type: NotesCategory
        if cate == None:
            return []
        return cate.notes

    @classmethod
    def getNotesById(cls,id):
        return session.query(NotesCategory).filter_by(id=id).first()

    @classmethod
    def add(cls,name):
        cate = cls(name=name)
        session.add(cate)
        session.commit()
        return True

