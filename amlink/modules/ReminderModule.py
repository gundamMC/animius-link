from .ReminderModel import Reminders,RemindersCategory
from . import ReminderModel
from database_controller import createTables,checkDatabase

def initdb():
    if not checkDatabase(Reminders,RemindersCategory)[0]:
        createTables()


def closedb():
    ReminderModel.session.close()


def reminder_look_up(name_entity_data, user):
    pass

register_intents = {
    "reminder":reminder_look_up,
}

start = initdb
end = closedb