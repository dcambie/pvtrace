from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

db_folder = os.path.join(os.path.expanduser('~'), 'pvtrace_data')

logger = logging.getLogger('pvtrace')
logfile = os.path.join(db_folder, 'log.txt')
logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO)

db = pvtrace.PhotonDatabase(None)

# Array with count of reflected photons
reflection_counter = []

for loop_i in range(0, 26):
    # Get DB filename
    filename = os.path.join(db_folder, 'reflection_lr305_'+str(loop_i*10), 'db.sqlite')

    # DO NOT use db.load() as it will change the db to the file which will eventually get db.empty() later, LOSING DATA!
    # db.load(filename)
    db.add_db_file(filename=filename, tables=("photon", "state"))
    reflection_counter.append(db.count_top_reflections()[0])
    db.empty()

print(reflection_counter)
logger.info('Reflection array (csv): ' + str(reflection_counter))

sys.exit(0)
