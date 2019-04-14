from amlink.database_controller import createTables, checkDatabase
from . import ReminderModel
from .ReminderModel import Reminders, RemindersCategory


def initdb():
    if not checkDatabase(Reminders, RemindersCategory)[0]:
        createTables()


def closedb():
    ReminderModel.session.close()


def reminder_look_up(name_entity_data, user):
    content = ''
    reminder = Reminders.seachByContext(user, content)
    detail = reminder.detail
    time = reminder.time
    deadline = reminder.ddl
    status = reminder.status
    returntext = detail

    return returntext


def add_reminder(name_entity_data, user):
    detail = ''
    content = ''
    category = ''
    dl = ''

    if detail == '':
        detail = content[:10]

    Reminders.add(user, content, detail, dl, category)


def del_reminder(name_entity_data, user):
    context = ''
    reminder = Reminders.seachByContext(user, context)
    Reminders.delete(reminder)


register_intents = {
    "reminder": reminder_look_up,
}

start = initdb
end = closedb
