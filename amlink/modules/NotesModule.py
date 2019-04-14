from amlink.database_controller import createTables, checkDatabase
from . import NotesModel
from .NotesModel import Notes, NotesCategory


def initdb():
    if not checkDatabase(Notes, NotesCategory)[0]:
        createTables()


def closedb():
    NotesModel.session.close()


def note_look_up(name_entity_data, user):
    pass


register_intents = {
    "note": note_look_up,
}

start = initdb
end = closedb
