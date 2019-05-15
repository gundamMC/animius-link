import time

from sqlalchemy import Column, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from amlink.database_controller import Base, initSession

session = initSession()


class Reminders(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, autoincrement=True, primary_key=True)
    content = Column(Text)
    detail = Column(Text)
    time = Column(Integer)
    deadline = Column(Integer)
    status = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("reminders_category.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    @classmethod
    def getAll(cls, user, finish=False, desc=False):
        if desc:
            return session.query(cls).filter_by(user_id=user.id, status=finish).order_by(cls.id.desc()).all()
        return session.query(cls).filter_by(user_id=user.id, status=finish).all()

    @classmethod
    def getByCategory(cls, user, cate, finish=False, desc=False):
        if desc:
            return session.query(cls).filter_by(user_id=user.id, category_id=cate.id, status=finish).order_by(
                cls.id.desc()).all()
        return session.query(cls).filter_by(user_id=user.id, category_id=cate.id, status=finish).all()

    @classmethod
    def seachByContext(cls, user, content):
        """
        :param user: User object
        :param content:
        :return:
        """
        return session.query(cls).filter_by(user_id=user.id, content=content).all()

    @property
    def overtime(self):
        return time.time() > self.deadline

    @classmethod
    def add(cls, user, content, detail, dl, category):
        """
        :param user: User object
        :param content: text
        :param detail: text
        :param dl: int unix time
        :param category: RemindersCategory object
        :return:
        """
        rmd = cls(user_id=user.id, content=content, detail=detail, deadline=dl, time=int(time.time()),
                  category_id=category.id)
        session.add(rmd)
        session.commit()
        return rmd

    @classmethod
    def delete(cls, reminder):
        session.delete(reminder)

    def finish(self):
        self.status = True
        session.commit()
        return True

    def dumpToDict(self):
        d = dict()
        d["id"] = self.id
        d["content"] = self.content
        d["detail"] = self.detail
        d["createtime"] = self.time
        d["deadline"] = self.deadline
        d["status"] = self.status
        d["category_name"] = self.category.name
        return d


class RemindersCategory(Base):
    __tablename__ = 'reminders_category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    notes = relationship("Reminders", backref='category', lazy='dynamic')

    @classmethod
    def getByName(cls, user, name):
        return session.query(cls).filter_by(user_id=user.id, name=name).first()

    @classmethod
    def getRemindersByName(cls, user, name):
        cate = cls.getByName(user, name)
        if cate is None:
            return []
        return cate.notes

    @classmethod
    def add(cls, user, name):
        cate = cls.getByName(user, name)
        if cate is not None:
            return None
        cate = cls(user_id=user.id, name=name)
        session.add(cate)
        session.commit()
        return cate

    @property
    def dumpToDict(self):
        d = dict()
        d["id"] = self.id
        d["name"] = self.name
        return d
