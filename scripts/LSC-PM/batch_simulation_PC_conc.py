from __future__ import division
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
from math import pow

photocatalyst = 'MB'
dye = 'Red305'
dye_conc = 100

file_path = os.path.join(os.path.expanduser('~'), 'pvtrace_data',
                         'MB_grad_'+str(dye_conc)+'.txt')

for mainloop_i in range(9, 11):
    exp = (-50 + mainloop_i)/10
    pc_conc = pow(10, exp)

    # This implicitly restart logging on the new location
    scene = pvtrace.Scene(dye+'_'+str(dye_conc)+'_'+photocatalyst+'_10_' + str(exp))

    logger = logging.getLogger('pvtrace')

    luminophore = LuminophoreMaterial(dye, dye_conc)
    pdms = Matrix('pdms')

    reactor = Reactor(reactor_name="5x5_6ch_squared", luminophore=luminophore, matrix=pdms, photocatalyst=photocatalyst,
                      photocatalyst_concentration=pc_conc, solvent="acetonitrile")
    scene.add_objects(reactor.scene_obj)

    lamp = LightSource(lamp_type='SolarSimulator')
    lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)
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
        text = str(scene.stats.print_excel_header("Concentration")+"\n")
    else:
        text = ""
    text += str(scene.stats.print_excel(pc_conc) + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)
