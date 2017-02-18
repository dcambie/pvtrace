from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

luminophore_name = 'Red305'
solvent = 'ACN'

file_path = os.path.join(os.path.expanduser('~'), 'pvtrace_data',
                         'output_'+luminophore_name+'_gradient_'+solvent+'.txt')

# Loop 0 to 250ppm
for mainloop_i in range(0, 26):
    luminophore_conc = mainloop_i * 10

    # This implicitly restart logging on the new location
    scene = pvtrace.Scene(luminophore_name + '_' + str(luminophore_conc) + '_' + solvent)

    logger = logging.getLogger('pvtrace')
    luminophore = LuminophoreMaterial(luminophore_name, luminophore_conc)
    pdms = Matrix('pdms')

    reactor = Reactor(reactor_name="5x5_6ch_squared", luminophore=luminophore, matrix=pdms, photocatalyst="MB",
                      photocatalyst_concentration=0, solvent=solvent)
    scene.add_objects(reactor.scene_obj)

    lamp = LightSource(lamp_type='SolarSimulator')
    lamp.set_lightsource()
    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100000, use_visualiser=False,
                           show_axis=True, show_counter=False, db_split=True, preserve_db_tables=True)

    # Run simulation
    tic = time.clock()
    logger.info('Simulation Started (time: '+str(tic)+')')
    trace.start()
    toc = time.clock()
    logger.info('Simulation Ended (time: '+str(toc)+', elapsed: '+str(toc-tic)+' s)')

    scene.stats.print_detailed()
    if mainloop_i == 0:
        text = str(scene.stats.print_excel_header("Luminophore conc.")+"\n")
    else:
        text = ""
    text += str(scene.stats.print_excel(luminophore_conc) + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)