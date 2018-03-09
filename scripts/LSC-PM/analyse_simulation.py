from __future__ import division
from pvtrace import *
textws = ''

import numpy as np
file_path = os.path.join('C:/','LSC_PM_simulation_results', 'Red_PMMA_10x10x0.3_1M', 'tubing_analysis.txt')
study = Scene(uuid= 'Red_PMMA_10x10x0.3_1M', force=True, level=logging.INFO)
logger = logging.getLogger('pvtrace.postrun_analysis')

# PHOTON BALANCE STUDY
# a = study.stats.calculate_photon_balance()
# study.stats.save_photon_balance(a, uuid)
# tic = time.clock()
study.stats.db_stats()
# uids = study.stats.db.endpoint_uids()
uids = study.stats.uids['tot']
text = study.stats.db.wavelength_for_uid(uids)

# To speed up calculation sample a subset of 1k photons
# uids = np.sort(uids)
# uids = list(uids[0:10])
numuid_c0 = len(text)

z = [0]*350
print(numuid_c0)

write_me = open(file_path, 'a')
for i in text:
    for g in range(1,350):
        g_wave = g*1 + 350
        if i >= g_wave - 1 and i <= g_wave:
            z[g] += 1

for i in z:
    write_me.write(str(i) + '\n')
# write_me.write(text)
write_me.close()

sys.exit(0)




