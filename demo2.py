import database

database.session = database.DBSession()

#database.createTables()
user = database.Users.getByName("admin")
print(user.id,user.name)
#cate = database.NotesCategory.add(user,"default")
#cate = database.NotesCategory.add(user,"life")
#print(cate)

# database.Notes.add(user,"ceshi","23131312",database.NotesCategory.getByName(user,"default"))
# database.Notes.add(user,"ceshi1","23131312",database.NotesCategory.getByName(user,"default"))
# database.Notes.add(user,"ceshi2","23131312",database.NotesCategory.getByName(user,"default"))
# database.Notes.add(user,"ceshil","23131312ll",database.NotesCategory.getByName(user,"life"))
# database.Notes.add(user,"ceshi1l","23131312lll",database.NotesCategory.getByName(user,"life"))
# database.Notes.add(user,"ceshi2l","23131312llll",database.NotesCategory.getByName(user,"life"))
print("totalnotes",user.notes.count())
for note in user.notes:
    print("-" * 3)
    print("title",note.title)
    print("time",note.time)
    print("cate",note.category.name)
    print(note.note)
    print()

print("total categoty",user.notes_category.count())
for cate in user.notes_category:
    print("*"*3)
    print("category name",cate.name)
    print("total notes",cate.notes.count())
    for note in cate.notes:
        print("-" * 3)
        print("title", note.title)
        print("time", note.time)
        print("cate", note.category.name)
        print(note.note)
    print("8"*3)
database.session.close()

