from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

file_path = os.path.join(os.path.expanduser('~'), 'pvtrace_data',
                         'output_Fang_whiteLEDs.txt')

reactors_to_test = ('5x5_fang_2ch',
                    '5x5_fang_4ch',
                    '5x5_fang_8ch',
                    '5x5_fang_12ch',
                    '5x5_fang_16ch',
                    '5x5_fang_20ch')
first = True
for reactor_name in reactors_to_test:
    # This implicitly restart logging on the new location
    scene = pvtrace.Scene(str(reactor_name) + '_whiteLED_9V_1k')
    logger = logging.getLogger('pvtrace')

    # LR305 200ppm in PDMS
    lr305 = LuminophoreMaterial('Red305', 200)
    pdms = Matrix('pdms')

    reactor = Reactor(reactor_name=reactor_name, luminophore=lr305, matrix=pdms, photocatalyst="MB",
                      photocatalyst_concentration=0.0004, solvent="acetonitrile")
    scene.add_objects(reactor.scene_obj)

    # Blue LEDs 9V
    lamp = LightSource(lamp_type='White LEDs')
    lamp.set_LED_voltage(voltage=9)
    lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)

    # Trace!
    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100000, use_visualiser=False,
                           show_axis=True, show_counter=False, db_split=True, preserve_db_tables=True)

    # Run simulation
    tic = time.clock()
    logger.info('Simulation Started (time: '+str(tic)+')')
    trace.start()
    toc = time.clock()
    logger.info('Simulation Ended (time: '+str(toc)+', elapsed: '+str(toc-tic)+' s)')

    scene.stats.print_detailed()
    if first is True:
        text = str(scene.stats.print_excel_header("Ractor")+"\n")
        first = False
    else:
        text = ""
    text += str(scene.stats.print_excel(reactor_name) + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)
