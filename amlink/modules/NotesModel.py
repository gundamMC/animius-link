import time

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from amlink.database_controller import Base, initSession

session = initSession()


class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(Text, index=True)
    note = Column(Text)
    time = Column(Integer)
    category_id = Column(Integer, ForeignKey("note_category.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    @classmethod
    def getLatest(cls, user, num=1):
        """
        :param user: User object
        :param num:
        :return:
        """
        return session.query(cls).filter_by(user_id=user.id).order_by(cls.id.desc()).limit(num).all()

    @classmethod
    def getAll(cls, user, desc=True):
        """
        :param user: User object
        :return:
        """
        if desc:
            return session.query(cls).filter_by(user_id=user.id).order_by(cls.id.desc()).all()
        return session.query(cls).filter_by(user_id=user.id).all()

    @classmethod
    def getByCategory(cls, user, cate, desc=True):
        if desc:
            return session.query(cls).filter_by(user_id=user.id, category_id=cate.id).order_by(cls.id.desc()).all()
        return session.query(cls).filter_by(user_id=user.id, category_id=cate.id).all()

    @classmethod
    def seachByTitle(cls, user, title):
        """
        :param user: User object
        :param title:
        :return:
        """
        return session.query(Notes).filter_by(user_id=user.id, title=title).all()

    @classmethod
    def add(cls, user, title, note, category):
        note0 = cls(title=title, note=note, time=int(time.time()), category_id=category.id, user_id=user.id)
        session.add(note0)
        session.commit()
        return note0

    @classmethod
    def delete(cls, note):
        session.delete(note)

    def dumpToDict(self):
        d = {}
        d["id"] = self.id
        d["title"] = self.title
        d["note"] = self.note
        d["createtime"] = self.time
        d["category_name"] = self.category.name
        return d


class NotesCategory(Base):
    __tablename__ = 'note_category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = relationship("Notes", backref='category', lazy='dynamic')

    @classmethod
    def getByName(cls, user, name):
        return session.query(cls).filter_by(user_id=user.id, name=name).first()

    @classmethod
    def add(cls, user, name):
        cate = cls.getByName(user, name)
        if cate != None:
            return None
        cate = cls(user_id=user.id, name=name)
        session.add(cate)
        session.commit()
        return cate

    def dumpToDict(self):
        d = {}
        d["id"] = self.id
        d["name"] = self.name
        d["notes_num"] = self.notes.count()
        return d
