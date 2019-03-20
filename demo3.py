from database import Reminders,RemindersCategory
import database,time
#database.createTables()
database.session = database.DBSession()
user = database.Users.getByName("admin")
cate = RemindersCategory.getByName(user,"default")
print(cate.name)
# a = Reminders.add(user,"play game","",int(time.time())+5000,cate)
# a.finish()
for r in Reminders.getAll(user):
    print(r.content)
for r in Reminders.getAll(user,finish=True):
    print(r.content)
database.session.close()