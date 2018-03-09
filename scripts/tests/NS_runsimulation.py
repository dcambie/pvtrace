# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
# blue red thickness: 3mm green: 4mm
# blue not yet, green EY, red Methylene Blue,
# set episilon to prevent the possibility of matching fate and generate
file_path = os.path.join('C:/', 'LSC_PM_simulation_results', 'pvtrace_smarts', 'WENS_PMMA_1220_ch', 'NS', 'pvtrace_result.txt')

# scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_rebuttal2_6")


# Create LSC-PM DYE material
Ev_lr305 = LuminophoreMaterial('Evonik_lr305', 1)#red
lr305 = LuminophoreMaterial('Red305', 200)#red
k160 = LuminophoreMaterial('K160', 1)#green
blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)#blue
# Create polymeric matrix
pdms = Matrix('pdms')
pmma = Matrix('PMMA')

solarposition_file = os.path.join(PVTDATA, 'smarts', 'dec22_solarposition.txt')
position_data = np.loadtxt(solarposition_file)
position_x = np.array(position_data[:, 0], dtype=np.float32)
position_y = np.array(position_data[:, 1], dtype=np.float32)
position_z = np.array(position_data[:, 2], dtype=np.float32)

for mainloop_i in range(0, 8):

    hour_dec = 9 + mainloop_i*0.5
    scene = pvtrace.Scene(level=logging.INFO, uuid=str(hour_dec))
    logger = logging.getLogger('pvtrace')
# change the view in Visualizer.py
    reactor = Reactor(reactor_name="10x10_chong_thickness0.3cm", luminophore=Ev_lr305, matrix=pmma, photocatalyst="MB",
                      photocatalyst_concentration=0.0012, solvent='ACN')
    scene.add_objects(reactor.scene_obj)

    lamp = LightSource(lamp_type='SMARTSsolar_simulator', set_spectrumfile = 'dec22_' + str(hour_dec) + 'hr.txt')
    x_i =round(position_x[mainloop_i], 3)
    y_i = round(position_y[mainloop_i], 3)
    z_i = position_z[mainloop_i]

    light_vector = (x_i, y_i, z_i)
    lampmove_vector = (-x_i*0.025, -y_i*0.025) # 0.025 is equal to distance between lamp and top surface of LSC

    lamp.set_lightsource(lamp_direction=light_vector,
                         irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.025, smarts=True)
    lamp.move_lightsource(vector=lampmove_vector)

    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100000, use_visualiser=False,
                           show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
    # set color on Trace.py while visualizing


    # Run simulation

    trace.start()

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