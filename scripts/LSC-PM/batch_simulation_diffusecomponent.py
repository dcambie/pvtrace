# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
# blue red thickness: 3mm green: 4mm
# blue not yet, green EY, red Methylene Blue,
# set episilon to prevent the possibility of matching fate and generate


# scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_rebuttal2_6")

file_path = os.path.join('C:/', 'LSC_PM_simulation_results', 'pvtrace_smarts', 'diffuse', 'pvtrace_result.txt')
# Create LSC-PM DYE material
Ev_lr305 = LuminophoreMaterial('Evonik_lr305', 1)#red
k160 = LuminophoreMaterial('K160', 1)#green
blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)#blue
# Create polymeric matrix
pdms = Matrix('pdms')
pmma = Matrix('PMMA')

for mainloop_i in range(0, 16):
    filename_i = mainloop_i * 0.5 + 5
    scene = pvtrace.Scene(level=logging.INFO, uuid=str(filename_i))
    logger = logging.getLogger('pvtrace')
    reactor = Reactor(reactor_name="10x10_chong_thickness0.3cm", luminophore=Ev_lr305, matrix=pmma, photocatalyst="MB",
                      photocatalyst_concentration=0.004, solvent='ACN')
    scene.add_objects(reactor.scene_obj)
    # lamp = LightSource(lamp_type='White LEDs')
    # lamp.set_LED_voltage(voltage=8)
    # lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)
    lamp = LightSource(lamp_type='SMARTSsolar_simulator', set_spectrumfile='june21_'+str(filename_i)+'hr.txt')
    # fixed by chong in order to run the different reactor without altering the scripts
    # lamp.set_lightsource(irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.025)
    # lamp.set_lightsource(irradiated_area=(reactor.lsc.size[0], 0.15035), distance=0.025)
    # lamp.move_lightsource(vector=(0, 0.01735))
    lamp.set_sphericalight(centre=(0.05, 0.05, 0.0015), radius=0.5, diffuse=True)
    # lamp.move_lightsource(vector=(4.235*0.025, 1.743*0.025))
    # check whether spectrum is correct or not
    # scene.add_objects([lamp.source])

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
