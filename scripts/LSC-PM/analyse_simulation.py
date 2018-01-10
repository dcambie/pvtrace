from pvtrace import *
import numpy as np
uuid = '1sqm_2dir_2.5cm'

study = Scene(uuid=uuid, force=True, level=logging.INFO)
logger = logging.getLogger('pvtrace.postrun_analysis')

# PHOTON BALANCE STUDY
# a = study.stats.calculate_photon_balance()
# study.stats.save_photon_balance(a, uuid)
tic = time.clock()
study.stats.db_stats()
# uids = study.stats.db.endpoint_uids()
uids = study.stats.uids['luminescent_edges'] + study.stats.uids['luminescent_channel']

# To speed up calculation sample a subset of 1k photons
# uids = np.sort(uids)
# uids = list(uids[0:1000])

history = study.stats.history_from_uid(uid=uids)

path_length = []
trj_list = study.stats.describe_trajectory(uid_list=history)
for trajectory in trj_list:
    path_length.append(trajectory.total_pathlength())
avg = np.mean(path_length)
logger.info("The average Photon-path Lumi_edge + Lumi_channels is "+str(avg*100)+"cm")

toc = time.clock()
logger.info('Calculating this took ' + str(toc - tic) + ' seconds!')

sys.exit(0)
