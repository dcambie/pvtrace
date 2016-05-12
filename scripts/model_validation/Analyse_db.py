import pvtrace
import os

a = pvtrace.Scene(uuid='6ch_Air_0.20dye', force=True)
db = pvtrace.PhotonDatabase.PhotonDatabase(dbfile=None)
db.add_db_file(filename=os.path.join(a.working_dir, 'db.sqlite'))
print(a.working_dir+"db.sqlite")
a.stats.add_db(db)
a.stats.print_detailed()
# a.stats.create_graphs()