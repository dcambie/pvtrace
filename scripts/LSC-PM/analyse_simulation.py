from pvtrace import *

study = Scene(uuid="gqgnmHLYG4rdeuPh5bAQtR", force=True)
# study.stats.print_detailed()
uids = study.stats.db.endpoint_uids()
a=study.stats.history_from_uid(uid=(63, 6, 125))

trjs=study.stats.describe_trajectory(uid_list=a)

dis = []
for trj in trjs:
    trj.pathlength_per_obj()
    #dis.append(trj.total_pathlength())



print(dis)
sys.exit(0)
