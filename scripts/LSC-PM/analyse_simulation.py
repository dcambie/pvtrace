from pvtrace import *

study = Scene(uuid="A3kggZUogY7cwRrR7VDCmk", force=True)

# db = pvtrace.PhotonDatabase(dbfile=None)
# db.add_db_file(filename=os.path.join(study.working_dir, 'db.sqlite'))
# study.stats.add_db(db)
# study.stats.print_detailed()

a = study.stats.calculate_photon_balance()
study.stats.save_photon_balance(a, 'photon_balance')
#uids = study.stats.db.endpoint_uids()
#a=study.stats.history_from_uid(uid=(63, 6, 125))

#trjs=study.stats.describe_trajectory(uid_list=a)

#dis = []
#for trj in trjs:
#    trj.pathlength_per_obj()
    # dis.append(trj.total_pathlength())
#print(dis)

sys.exit(0)
