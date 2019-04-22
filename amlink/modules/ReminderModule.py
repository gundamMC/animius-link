from amlink.database_controller import createTables, checkDatabase
from . import ReminderModel
from .ReminderModel import Reminders, RemindersCategory


def initdb():
    if not checkDatabase(Reminders, RemindersCategory)[0]:
        createTables()


def closedb():
    ReminderModel.session.close()


def reminder_look_up(name_entity_data, user):
    content = name_entity_data['title']
    reminder = Reminders.seachByContext(user, content)
    detail = reminder.detail
    time = reminder.time
    deadline = reminder.ddl
    status = reminder.status

    dict = {"content": content,
            "time": time,
            "detail": detail,
            "deadline": deadline,
            "status": status,
            }

    return dict


def add_reminder(name_entity_data, user):
    detail = name_entity_data['title']
    content = name_entity_data['title']
    category = 'main'
    dl = name_entity_data['time']

    if detail == '':
        detail = content[:10]

    Reminders.add(user, content, detail, dl, category)
    dict = {"content": content,
            "deadline": dl,
            "detail": detail,
            "category": category
            }
    return dict


def del_reminder(name_entity_data, user):
    context = name_entity_data['title']
    reminder = Reminders.seachByContext(user, context)
    Reminders.delete(reminder)
    return {}


register_intents = {
    "reminder": reminder_look_up,
    "add reminder": add_reminder,
    "delete reminder": del_reminder
}

start = initdb
end = closedb
