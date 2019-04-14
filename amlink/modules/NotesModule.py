from amlink.database_controller import createTables, checkDatabase
from . import NotesModel
from .NotesModel import Notes, NotesCategory


def initdb():
    if not checkDatabase(Notes, NotesCategory)[0]:
        createTables()


def closedb():
    NotesModel.session.close()


def note_look_up(name_entity_data, user):
    title = ''
    note = Notes.seachByTitle(user, title)
    text = note.text
    time = note.time
    returntext = text

    return returntext


def add_note(name_entity_data, user):
    title = ''
    note = ''
    category = ''
    if title == '':
        title = note[:10]

    Notes.add(user, title, note, category)


def del_note(name_entity_data, user):
    title = ''
    note = Notes.seachByTitle(user, title)
    Notes.delete(note)


register_intents = {
    "note": note_look_up,
}

start = initdb
end = closedb
