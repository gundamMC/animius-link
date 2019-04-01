from .EssentialModel import Users
from database_controller import createTables,checkDatabase
from . import EssentialModel

def initdb():
    if not checkDatabase(Users)[0]:
        createTables()

def closedb():
    EssentialModel.session.close()


def user_look_up(name_entity_data, user):
    pass

def user_get(name):
    return Users.getByName(name)


register_intents = {
    "user":user_look_up,
    "user_get": user_get
}

start = initdb
end = closedb