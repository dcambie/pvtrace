from __future__ import division
import numpy as np
import sys
# import logging
from pvtrace.external import transformations as tf
from pvtrace import *
import time
from Modules import *

# 1 unit = 1 mm
scene = Scene()

reactor = Reactor(name="5x5_8ch", dye="Red305", dye_concentration=0.15, photocatalyst="MB")
for obj in reactor.scene_obj:
    scene.add_object(obj)

# Ask python that the directory of this script file is and use it as the location of the database file
pwd = os.getcwd()
dbfile = os.path.join(pwd, 'pvtracedb.sql')  # <--- the name of the database file, with "pvtracedb" overwrite is implied

trace = Tracer(scene=scene, source=source, seed=None, throws=10, database_file=dbfile, use_visualiser=false, show_log=false, show_axis=True)
trace.show_lines = true
trace.show_path = true

# Run simulation
tic = time.clock()
trace.start()
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

sys.exit(0)
