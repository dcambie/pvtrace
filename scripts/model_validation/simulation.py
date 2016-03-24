from __future__ import division
# import subprocess
import logging
import time
from Modules import *

# 1 unit = 1 m  Albeit not convenient, this assumption is deeply bounded in pvtrace's heart
# scene = Scene('overwrite_me')
scene = Scene()
logger = logging.getLogger('pvtrace')

# reactor = Reactor(reactor_name="5x5_6ch_squared", dye="Red305", dye_concentration=0.20, photocatalyst="MB",
#                   photocatalyst_concentration=0.0004)
reactor = Reactor(reactor_name="5x5_slab", dye="Red305", dye_concentration=0.20, photocatalyst="Air",
                  photocatalyst_concentration=0.0004)
logger.info('Reactor volume (calculated): '+str(reactor.reaction_volume*1000000)+' mL')

# reactor = Reactor(name="5x5_0ch", dye="Red305", dye_concentration=0.20)
for obj in reactor.scene_obj:
    scene.add_object(obj)

# Doesn't save DB file but uses RAM disk for faster simulation
# file = os.path.join(os.path.expanduser("~"),"pvtracedb.sql")
# file = None
trace = Tracer(scene=scene, source=reactor.source, seed=None, throws=500000, use_visualiser=False,
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
plane = Plane()
plane.name= 'base for render'
# scene.add_object(plane)
# scene.pov_render(camera_position=(-0.05, 0.025, 0.05), camera_target=(0.025, 0.025, 0), height=1080, width=1920)
#stats.history()
#stats.save_db()


sys.exit(0)


