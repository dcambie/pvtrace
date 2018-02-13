from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

lr305 = LuminophoreMaterial('Red305', 200)
solvent = 'ACN'
pdms = Matrix('pdms')
pmma = Matrix('pmma')
file_path = os.path.join('D:/', 'pvtrace_chongRI_ACN1.38', 'pvtrace_chong_result.txt')

# Loop 0 to 250ppm
for mainloop_i in range(0, 16):
    refractive_c = mainloop_i / 100 + 1.30

    # This implicitly restart logging on the new location
    scene = pvtrace.Scene(uuid=str(refractive_c))

    logger = logging.getLogger('pvtrace')

    reactor = Reactor(reactor_name="10x10_chong_thickness0.3cm", luminophore=lr305, matrix=pdms, photocatalyst="MB",
                      photocatalyst_concentration=0.004, solvent=solvent, refractive_index_cgchong=refractive_c)
    scene.add_objects(reactor.scene_obj)

    lamp = LightSource(lamp_type='SolarSimulator')
    lamp.set_lightsource()
    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100000, use_visualiser=False,
                           show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)

    # Run simulation
    tic = time.clock()
    logger.info('Simulation Started (time: '+str(tic)+')')
    trace.start()
    toc = time.clock()
    logger.info('Simulation Ended (time: '+str(toc)+', elapsed: '+str(toc-tic)+' s)')

    scene.stats.print_detailed()
    if mainloop_i == 0:
        text = str(scene.stats.print_excel_header()+"\n")
    else:
        text = ""
    text += str(scene.stats.print_excel() + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)
