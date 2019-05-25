from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

conn = "sqlite:///Animius_Link.db"
Base = declarative_base()


def checkDatabase(*tables):
    try:
        engine = create_engine(conn)
        DBSession = sessionmaker(bind=engine)
        dbs = DBSession()
        for t in tables:
            dbs.query(t).first()
        return True, 0, ""
    except ProgrammingError as err:
        return False, err.code, err.orig
    except:
        return False, -1, ""


def initSession():
    global session, DBSession
    engine = create_engine(conn)
    DBSession = scoped_session(sessionmaker(bind=engine))
    session = DBSession()
    return session


def closeSession():
    global session, DBSession
    session.close()
    DBSession.remove()


def createTables():
    try:
        engine = create_engine(conn)
        sessionmaker(bind=engine)().execute("PRAGMA foreign_keys = ON")
        Base.metadata.create_all(engine)
        return True
    except:
        return False
