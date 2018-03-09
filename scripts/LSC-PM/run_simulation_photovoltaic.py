# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
# blue red thickness: 3mm green: 4mm
# blue not yet, green EY, red Methylene Blue,
# set episilon to prevent the possibility of matching fate and generate
file_path = os.path.join('C:/','LSC_PM_simulation_results', 'photovoltaic', 'PV_redLSC_PM', 'simulation_results.txt')

# scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_rebuttal2_6")
scene = pvtrace.Scene(level=logging.INFO, uuid='overwrite_me')
logger = logging.getLogger('pvtrace')

# Create LSC-PM DYE material
Ev_lr305 = LuminophoreMaterial('Evonik_lr305', 1)#red
k160 = LuminophoreMaterial('K160', 1)#green
blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)#blue
# Create polymeric matrix
pdms = Matrix('pdms')
pmma = Matrix('PMMA')

# !!Change the LSC material while simulating the blank LSC
reactor = Reactor(reactor_name="10x10_chong_thickness0.3cm", luminophore=Ev_lr305, matrix=pmma, photocatalyst="MB",
                  photocatalyst_concentration=0.0012, solvent='ACN', exist_photovoltaic=True, blank=False)
scene.add_objects(reactor.scene_obj)

# lamp = LightSource(lamp_type='White LEDs')
# lamp.set_LED_voltage(voltage=8)
# lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)
lamp = LightSource(lamp_type='Sun')

lamp.set_lightsource(irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.025)
# lamp.set_lightsource(irradiated_area=(reactor.lsc.size[0], 0.15035), distance=0.025)
# lamp.move_lightsource(vector=(0, 0.01735))

trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100, use_visualiser=True,
                       show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
# set color on Trace.py while visualizing

# Run simulation

trace.start()

scene.stats.print_detailed()
text = str(scene.stats.print_excel(backscatter=False) + "\n")
write_me = open(file_path, 'a')
write_me.write(text)
write_me.close()

sys.exit(0)

