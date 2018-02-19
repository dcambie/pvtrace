# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
# blue red thickness: 3mm green: 4mm
# blue not yet, green EY, red Methylene Blue,
# set episilon to prevent the possibility of matching fate and generate
file_path = os.path.join('D:/', 'pvtrace_smarts', 'WEtry', 'pvtrace_result.txt')

# scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_rebuttal2_6")


# Create LSC-PM DYE material
lr305 = LuminophoreMaterial('Red305', 200)#red
k160 = LuminophoreMaterial('K160', 1)#green
blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)#blue
# Create polymeric matrix
pdms = Matrix('pdms')
pmma = Matrix('PMMA')

solarposition_file = os.path.join(PVTDATA, 'smarts', 'june21_solarposition.txt')
position_data = np.loadtxt(solarposition_file)
position_x = np.array(position_data[:, 0], dtype=np.float32)
position_y = np.array(position_data[:, 1], dtype=np.float32)
position_z = np.array(position_data[:, 2], dtype=np.float32)

for mainloop_i in range(8, 12):

    hour_june = 5 + mainloop_i*0.5
    scene = pvtrace.Scene(level=logging.INFO, uuid=str(hour_june))
    logger = logging.getLogger('pvtrace')

    reactor = Reactor(reactor_name="10x10_chong_thickness0.3cm_WE", luminophore=lr305, matrix=pmma, photocatalyst="MB",
                      photocatalyst_concentration=0.004, solvent='ACN')
    scene.add_objects(reactor.scene_obj)

    lamp = LightSource(lamp_type='SMARTSsolar_simulator', set_spectrumfile = 'june21_' + str(hour_june) + 'hr.txt')
    x_i =round(position_x[mainloop_i], 3)
    y_i = round(position_y[mainloop_i], 3)
    z_i = position_z[mainloop_i]

    light_vector = (x_i, y_i, z_i)
    lampmove_vector = (-x_i*0.025, -y_i*0.025)

    lamp.set_lightsource(lamp_direction=light_vector,
                         irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.025, smarts=True)
    lamp.move_lightsource(vector=lampmove_vector)

    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100, use_visualiser=False,
                           show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
    # set color on Trace.py while visualizing


    # Run simulation
    tic = time.clock()
    logger.info('Simulation Started (time: ' + str(tic) + ')')
    trace.start()
    toc = time.clock()
    logger.info('Simulation Ended (time: ' + str(toc) + ', elapsed: ' + str(toc - tic) + ' s)')

    scene.stats.print_detailed()
    if mainloop_i == 0:
        text = str(scene.stats.print_excel_header() + "\n")
    else:
        text = ""
    text += str(scene.stats.print_excel() + "\n")
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()

sys.exit(0)
