from amlink.database_controller import createTables, checkDatabase
from . import ReminderModel
from .ReminderModel import Reminders, RemindersCategory


def initdb():
    if not checkDatabase(Reminders, RemindersCategory)[0]:
        createTables()


def closedb():
    ReminderModel.session.close()


def reminder_look_up(name_entity_data, user):
    pass


register_intents = {
    "reminder": reminder_look_up,
}

start = initdb
end = closedb
