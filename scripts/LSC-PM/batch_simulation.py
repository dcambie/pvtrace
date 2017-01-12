from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

file_path = os.path.join(os.path.expanduser('~'), 'pvtrace_data',
                         'output_reflection.txt')
for mainloop_i in range(1, 26):
    lr305_conc = mainloop_i*10

    # This implicitly restart logging on the new location
    scene = pvtrace.Scene('reflection_lr305_' + str(lr305_conc))

    logger = logging.getLogger('pvtrace')
    lr305 = LuminophoreMaterial('Red305', lr305_conc)
    pdms = Matrix('pdms')

    reactor = Reactor(reactor_name="5x5_6ch_squared", luminophore=lr305, matrix=pdms, photocatalyst="MB",
                      photocatalyst_concentration=0.0004)
    scene.add_objects(reactor.scene_obj)

    lamp = LightSource(lamp_type='SolarSimulator', irradiated_area=(0.05, 0.05), distance=0.025)
    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=1000000, use_visualiser=False,
                           show_axis=True, show_counter=False, db_split=True, preserve_db_tables=True)

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
    text += str(scene.stats.print_excel(lr305_conc) + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)
