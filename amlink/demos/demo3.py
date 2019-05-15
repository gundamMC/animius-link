from amlink.modules import database as db

db.initSession()

user = db.Users.getByName("admin")
cate = db.RemindersCategory.getByName(user,"default")
print(cate.name)
print(cate.dumpToDict())
# a = Reminders.add(user,"play game","",int(time.time())+5000,cate)
# a.finish()
for r in db.Reminders.getAll(user):
    print(r.content)
    print(r.dumpToDict())
for r in db.Reminders.getAll(user,finish=True):
    print(r.content)

db.closeSession()