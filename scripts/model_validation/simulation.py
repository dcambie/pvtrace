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

# trace = Tracer(scene=scene, source=source, seed=None, database_file=dbfile, throws=250, use_visualiser=True, show_log=False)
# trace.show_lines = True
# trace.show_path = True
# import time
# tic = time.clock()
# trace.start()
# toc = time.clock()

sys.exit(0)
