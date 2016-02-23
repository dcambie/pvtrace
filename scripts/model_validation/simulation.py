from __future__ import division
import numpy as np
import sys
# import logging
from pvtrace.external import transformations as tf
from pvtrace import *
import time
from Modules import *

#PVTDATA = '/home/dario/pvtrace' # Hack needed for running simulations on /tmp from VM

# 1 unit = 1 m  Albeit not convenient, this assumption is deeply bounded in pvtrace's hearth

scene = Scene()

reactor = Reactor(reactor_name="5x5_8ch", dye="Red305", dye_concentration=0.20, photocatalyst="MB", photocatalyst_concentration=0.0004)
# reactor = Reactor(name="5x5_0ch", dye="Red305", dye_concentration=0.20)
for obj in reactor.scene_obj:
    scene.add_object(obj)

# Ask python that the directory of this script file is and use it as the location of the database file
pwd = os.getcwd()
dbfile = os.path.join(pwd, 'pvtracedb.sql')  # <--- the name of the database file, with "pvtracedb" overwrite is implied

trace = Tracer(scene=scene, source=reactor.source, seed=None, throws=10, database_file=dbfile, use_visualiser=False, show_log=false, show_axis=True)
trace.show_lines = true
trace.show_path = true

# Run simulation
print 'Start simulation'
tic = time.clock()
trace.start()
print 'Simulation ended!'
toc = time.clock()

# For reproducibility reasons always append git version to results (tested on linux only)
import subprocess
label = subprocess.check_output(["git", "describe"], cwd=PVTDATA)
print 'PvTrace ', label,  ' simulation ended'
print 'Date/Time ', time.strftime("%c")
print 'Run Time: ', toc - tic, ' sec.(s)'
print ''


stats = Statistics(trace.database)
stats.print_report()
stats.print_detailed()
stats.create_graphs()

sys.exit(0)
