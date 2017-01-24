from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

db_folder = os.path.join(os.path.expanduser('~'), 'pvtrace_data', 'backup')

logger = logging.getLogger('pvtrace')
logfile = os.path.join(db_folder, 'log.txt')
logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)
tic = time.clock()
logger.info('Start merging')
db = pvtrace.PhotonDatabase(None)
count = 0

for loop_i in range(5, 10):
    filename = os.path.join(db_folder, '~pvtrace_tmp'+str(loop_i)+'.sql')

    db.add_db_file(filename=filename, tables=None)
    db.connection.commit()
    if 'toc' in locals():
        prev = toc
    else:
        prev = tic
    toc = time.clock()
    logger.info('Added '+str(loop_i)+' in ' + str(toc - prev) + ' s)')
    count += 1

toc = time.clock()
time_tot = toc - tic
logger.info('Total '+str(count)+' in ' + str(time_tot) + ' s (i.e. '+str(time_tot/count))

db.dump_to_file(os.path.join(db_folder, 'final.sql'))

final_tic = time.clock()
logger.info('Writing took  '+str(final_tic-toc)+'s  for  ' + str(count))
sys.exit(0)
