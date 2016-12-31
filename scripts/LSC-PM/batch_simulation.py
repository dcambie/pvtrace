from __future__ import division
# import subprocess
import logging
import time
import pvtrace
from modules import *
import sys

red305_concentration = 0.20

file_path = os.path.join(os.path.expanduser('~'), 'pvtrace_data',
                         'output_red_{0}_mb_conc.txt'.format(str(red305_concentration)))
for mainloop_i in range(0, 20):
    if mainloop_i < 10:
        mb_concentration = 0.00001 + 0.00001 * mainloop_i
    else:
        mb_concentration = 0.0001 + 0.0001 * (mainloop_i - 9)

    scene = pvtrace.Scene('conc_study_' + str(red305_concentration) + '_' + str(mb_concentration))
    logger = logging.getLogger('pvtrace')

    reactor = Reactor(reactor_name="5x5_square", dye="Red305", dye_concentration=red305_concentration,
                      photocatalyst="MB", photocatalyst_concentration=mb_concentration)
    for obj in reactor.scene_obj:
        scene.add_object(obj)

    # Doesn't save DB file but uses RAM disk for faster simulation
    # file = os.path.join(os.path.expanduser("~"),"pvtracedb.sql")
    # file = None
    trace = pvtrace.Tracer(scene=scene, source=reactor.source, seed=None, throws=20000, use_visualiser=False,
                           show_axis=True, show_counter=False, db_split=True)
    trace.show_lines = True
    trace.show_path = False

    # Run simulation
    tic = time.clock()
    logger.info('Simulation Started (time: '+str(tic)+')')
    trace.start()
    toc = time.clock()
    logger.info('Simulation Ended (time: '+str(toc)+', elapsed: '+str(toc-tic)+' s)')

    scene.stats.print_detailed()
    if mainloop_i == 0:
        text = str(scene.stats.print_excel_header("Concentration")+"\n")
    else:
        text = ""
    text += str(scene.stats.print_excel(mb_concentration) + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)
