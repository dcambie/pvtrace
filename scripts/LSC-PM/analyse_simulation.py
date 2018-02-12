from __future__ import division
from pvtrace import *
textws = ''
file_path = os.path.join('D:/', 'pvtrace_chongRI_ACN1.38', 'pvtrace_chong_result_differentcap.txt')
import numpy as np
for mainloop_i in range(7, 16):
    uuidis = mainloop_i / 100 + 1.30

    study = Scene(uuid=str(uuidis), force=True, level=logging.INFO)
    logger = logging.getLogger('pvtrace.postrun_analysis')

    # PHOTON BALANCE STUDY
    # a = study.stats.calculate_photon_balance()
    # study.stats.save_photon_balance(a, uuid)
    # tic = time.clock()
    study.stats.db_stats()
    # uids = study.stats.db.endpoint_uids()
    uids = study.stats.uids['capillary_0react']
    uids2 = study.stats.uids['capillary_3react']

    # To speed up calculation sample a subset of 1k photons
    # uids = np.sort(uids)
    # uids = list(uids[0:10])
    numuid_c0 = len(uids)
    numuid_c3 = len(uids2)
    diffuid = len(uids) - len(uids2)

    print("The refractive index of PFA is %.2f" % uuidis)
    print("The reaction photon taking place in capillary0 is %d" % numuid_c0)
    print("The reaction photon taking place in capillary3 is %d" % numuid_c3)
    print("The gap between two capillary is %d\n" % diffuid)


    textws = str("The refractive index of PFA is %.2f\n" % uuidis)
    textws += str("The reaction photon taking place in capillary0 is %d\n" % numuid_c0)
    textws += str("The reaction photon taking place in capillary3 is %d\n" % numuid_c3)
    textws += str("The gap between two capillary is %d\n\n" % diffuid)

    write_me = open(file_path, 'a')
    write_me.write(textws)
    write_me.close()


    '''
    history = study.stats.history_from_uid(uid=uids)
    
    path_length = []
    trj_list = study.stats.describe_trajectory(uid_list=history)
    for trajectory in trj_list:
    path_length.append(trajectory.total_pathlength())
    avg = np.mean(path_length)
    logger.info("The average Photon-path Lumi_edge + Lumi_channels is "+str(avg*100)+"cm")
    
    toc = time.clock()
    logger.info('Calculating this took ' + str(toc - tic) + ' seconds!')
    '''

sys.exit(0)
