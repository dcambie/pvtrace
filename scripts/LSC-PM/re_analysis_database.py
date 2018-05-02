from __future__ import division
from pvtrace import *
file_path = os.path.join('D:/','LSC_PM_simulation_results', 'photovoltaic', 'simulation_results.txt')
study = Scene(uuid='attatched_47x47x0.8_100k0314_3', force=True, level=logging.INFO)
logger = logging.getLogger('pvtrace.postrun_analysis')

# PHOTON BALANCE STUDY
# a = study.stats.calculate_photon_balance()
# study.stats.save_photon_balance(a, uuid)
# tic = time.clock()
study.stats.db_stats()
# uids = study.stats.db.endpoint_uids()
# uids_tot = study.stats.uids['find_bug']

study.stats.print_detailed()
text_No = 'attatched_47x47x0.8_100k0314_3\n'
text_head = str(study.stats.print_excel_header(photovoltaic=True) + "\n")
text = str(study.stats.print_excel(photovoltaic=True) + "\n")
write_me = open(file_path, 'a')
write_me.write(text_No)
write_me.write(text_head)
write_me.write(text)
write_me.close()