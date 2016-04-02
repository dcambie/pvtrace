from __future__ import division
# import subprocess
import logging
import time
import pvtrace
from modules import *
import sys

# 1 unit = 1 m  Albeit not convenient, this assumption is deeply bounded in pvtrace's heart
scene = pvtrace.Scene()
# scene = pvtrace.Scene('overwrite_me')

logger = logging.getLogger('pvtrace')

# 1/04 notes:
# 0.15 and 0.05 dye loading
# cat conc from 0.01 to 0.00001 every 10x

# reactor = Reactor(reactor_name="5x5_6ch_squared", dye="Red305", dye_concentration=0.20, photocatalyst="MB",
#                   photocatalyst_concentration=0.0004)
reactor = Reactor(reactor_name="5x5_1ch", dye="Red305", dye_concentration=0.15, photocatalyst="MB",
                  photocatalyst_concentration=0.01)
logger.info('Reactor volume (calculated): '+str(reactor.reaction_volume*1000000)+' mL')

# reactor = Reactor(name="5x5_0ch", dye="Red305", dye_concentration=0.20)
for obj in reactor.scene_obj:
    scene.add_object(obj)

# Doesn't save DB file but uses RAM disk for faster simulation
# file = os.path.join(os.path.expanduser("~"),"pvtracedb.sql")
# file = None
trace = pvtrace.Tracer(scene=scene, source=reactor.source, seed=None, throws=500000, use_visualiser=False,
                       show_log=False, show_axis=True, show_counter=False, db_split=True)
trace.show_lines = True
trace.show_path = False

# Run simulation
tic = time.clock()
logger.debug('Simulation Started (time: '+str(tic)+')')
trace.start()
toc = time.clock()
logger.debug('Simulation Ended (time: '+str(toc)+', elapsed: '+str(toc-tic)+' s)')

for obj in scene.objects:
    if type(obj) is pvtrace.Devices.LSC:
        spectrum = obj.spectrum(surface_names=('far', 'near', 'right', 'left'))
        print(spectrum)
# For reproducibility reasons always append git version to results (tested on linux only)
# label = subprocess.check_output(["git", "describe"], cwd=PVTDATA, shell = True)
# print 'PvTrace ', label,  ' simulation ended'

scene.stats.print_detailed()
# stats.print_excel()
scene.stats.create_graphs()
plane = pvtrace.Geometry.Plane()
plane.name = 'base for render'
# scene.add_object(plane)
# scene.pov_render(camera_position=(-0.05, 0.025, 0.05), camera_target=(0.025, 0.025, 0), height=1080, width=1920)
# stats.history()
# stats.save_db()

sys.exit(0)
