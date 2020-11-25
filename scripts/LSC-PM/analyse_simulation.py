from __future__ import division
from pvtrace import *

import numpy as np
file_path = os.path.join('D:/','LSC_PM_simulation_results', 'Red_PMMA_10x10x0.3_1M', 'tubing_analysis.txt')
study = Scene(uuid= 'Red_PMMA_10x10x0.3_1M', force=True, level=logging.INFO)
logger = logging.getLogger('pvtrace.postrun_analysis')

# PHOTON BALANCE STUDY
# a = study.stats.calculate_photon_balance()
# study.stats.save_photon_balance(a, uuid)
# tic = time.clock()
study.stats.db_stats()
# uids = study.stats.db.endpoint_uids()
uids_tot = study.stats.uids['tot']
uids_ref = study.stats.uids['']
text = study.stats.db.original_wavelength_for_uid(uids)

# To speed up calculation sample a subset of 1k photons
# uids = np.sort(uids)
# uids = list(uids[0:10])
numuid_c0 = len(uids)

z = [0]*350
print(numuid_c0)

write_me = open(file_path, 'a')
Energy_photon = 0
h_plank = 6.626 # 10(-34)
c_photon = 2.998 # 10(8)
for i in text:
    Energy_each = h_plank * c_photon / i # i nanometer 10**-9
    Energy_photon += Energy_each # 10**-17


    # for g in range(0,350):
    #     g_wave = g*1 + 350
    #     if i >= g_wave  and i <= g_wave + 1:
    #         z[g] += 1
#
# wavelength = 350
# for i in z:
#
#     write_me.write(str(wavelength) + '\t')
#     write_me.write(str(i) + '\n')
#     wavelength += 1
# # write_me.write(text)
# write_me.close()
#
# sys.exit(0)
#
print(Energy_photon)


