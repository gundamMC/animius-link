from . import DatabaseModel as db

def dbwrapper(func):
    def wrapper():
        db.initSession()
        func()
        db.closeSession()
    return wrapper()

@dbwrapper
def initdb():
    if not db.checkDatabase():
        db.createTables()

def autoselect(name_entity_data, user_id):
    # do something
    pass

@dbwrapper
def notes(name_entity_data, user_id):
    # do something
    if "sadf" == "!@3123":
        return db.Notes.getAll()
    pass

@dbwrapper
def reminders(name_entity_data, user_id):
    # do something
    pass

@dbwrapper
def getuser(username):
    return db.Users.getByName(username)

register_intents = {
    "db_init":initdb,
    "db_autoselect":autoselect,
    'notes': notes,
    "reminders":reminders,
    "getusers":getuser,
}