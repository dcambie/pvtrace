import pvtrace
import os

a = pvtrace.Scene(uuid='1ch', force=True)
db = pvtrace.PhotonDatabase.PhotonDatabase(dbfile=None)
db.add_db_file(filename=os.path.join(a.working_dir, 'db.sqlite'))
a.stats.add_db(db)
# a.stats.print_detailed()

print(a.stats.print_excel_header())
print(a.stats.print_excel())
