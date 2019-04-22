from amlink.database_controller import createTables, checkDatabase
from . import NotesModel
from .NotesModel import Notes, NotesCategory


def initdb():
    if not checkDatabase(Notes, NotesCategory)[0]:
        createTables()


def closedb():
    NotesModel.session.close()


def note_look_up(name_entity_data, user):
    title = name_entity_data['title']
    note = Notes.seachByTitle(user, title)
    text = note.text
    time = note.time
    dict = {"title": title,
            "text": text,
            "time": time
            }

    return dict


def add_note(name_entity_data, user):
    title = name_entity_data['title']
    note = name_entity_data['text']
    category = "main"
    if title == '':
        title = note[:10]

    Notes.add(user, title, note, category)

    dict = {"title": title,
            "text": note
            }

    return dict


def del_note(name_entity_data, user):
    title = name_entity_data['title']
    note = Notes.seachByTitle(user, title)
    Notes.delete(note)

    return {}


register_intents = {
    "note": note_look_up,
    "add note": add_note,
    "delete note": del_note
}

start = initdb
end = closedb
