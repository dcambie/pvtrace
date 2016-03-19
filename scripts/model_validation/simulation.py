from __future__ import division
# import subprocess
import time
from Modules import *
import logging

# 1 unit = 1 m  Albeit not convenient, this assumption is deeply bounded in pvtrace's heart
scene = Scene('LPVUDb2Rg9Ehe8SjHPFE6h')

LOG_FILENAME = os.path.join(scene.working_dir, 'output.log')
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('pvtrace')
logger.debug('*** NEW SIMULATION ***')
logger.info('UUID: '+scene.uuid)
logger.debug('Filename:'+__file__)
logger.debug('Date/Time '+time.strftime("%c"))

# reactor = Reactor(reactor_name="5x5_6ch_squared", dye="Red305", dye_concentration=0.20, photocatalyst="MB", photocatalyst_concentration=0.0004)
reactor = Reactor(reactor_name="5x5_6ch_squared", dye="Red305", dye_concentration=0.10, photocatalyst="Air", photocatalyst_concentration=0.0004)
logger.info('Reactor volume (calculated): '+str(reactor.reaction_volume*1000000)+' mL')

# reactor = Reactor(name="5x5_0ch", dye="Red305", dye_concentration=0.20)
for obj in reactor.scene_obj:
    scene.add_object(obj)

# Doesn't save DB file but uses RAM disk for faster simulation
# file = os.path.join(os.path.expanduser("~"),"pvtracedb.sql")
# file = None
trace = Tracer(scene=scene, source=reactor.source, seed=None, throws=50, use_visualiser=False,
               show_log=False, show_axis=True, show_counter=False, db_split=True)
trace.show_lines = true
trace.show_path = false

# Run simulation
tic = time.clock()
logger.debug('Simulation Started (time: '+str(tic)+')')
trace.start()
toc = time.clock()
logger.debug('Simulation Ended (time: '+str(toc)+', elapsed: '+str(toc-tic)+' s)')

# For reproducibility reasons always append git version to results (tested on linux only)
# label = subprocess.check_output(["git", "describe"], cwd=PVTDATA, shell = True)
# print 'PvTrace ', label,  ' simulation ended'

scene.stats.print_detailed()
#stats.print_excel()
scene.stats.create_graphs()
#stats.history()
#stats.saveDB()

# stats.get_bounces()

sys.exit(0)
