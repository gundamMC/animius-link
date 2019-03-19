import database

database.session = database.DBSession()

#database.createTables()

print(database.Notes.getAll()[0].title)
#database.NotesCategory.add("ceshi")
database.Notes.add("newnote","sdkhfkasdf",1)
notesindefault = database.NotesCategory.getNotesByName("default")
for note in notesindefault:
    print("-"*3)
    print("title",note.title)
    print("time",note.time)
    print("cate",note.category.name)
    print(note.note)
    print()

database.session.close()