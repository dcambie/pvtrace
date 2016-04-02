import pvtrace
import os

a = pvtrace.Scene(uuid='500k_1ch_MB_0.0001', force=True)
db = pvtrace.PhotonDatabase.PhotonDatabase(dbfile=None)
db.add_db_file(filename=os.path.join(a.working_dir, 'db.sqlite'))
print(a.working_dir+"db.sqlite")
a.stats.add_db(db)
a.stats.print_detailed()
a.stats.create_graphs()