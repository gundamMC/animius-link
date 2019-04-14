from sqlalchemy import Column, Integer, Text

from amlink.database_controller import Base, initSession

session = initSession()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text,nullable=False,unique=True,index=True)
    password = Column(Text,nullable=False,index=True)

    @classmethod
    def getByName(cls,name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def getById(cls,id):
        return session.query(cls).filter_by(id=id).first()

    def checkPassword(self,psd):
        return self.password == psd
