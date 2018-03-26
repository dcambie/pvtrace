# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
# blue red thickness: 3mm green: 4mm
# blue not yet, green EY, red Methylene Blue,
# set episilon to prevent the possibility of matching fate and generate
file_path = os.path.join('D:/','LSC_PM_simulation_results', 'test_tilt_LSC', 'simulation_results.txt')

# scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_rebuttal2_6")
scene = pvtrace.Scene(level=logging.INFO, uuid='overwrite_me')
logger = logging.getLogger('pvtrace')

# Create LSC-PM DYE material and host material
Lm_lr305 = LuminophoreMaterial('Limacryl_lr305', 1)#red
pmma = Matrix('PMMA')

# !!Change the LSC material while simulating the blank LSC
reactor = Reactor(reactor_name="47x47_chong_thickness0.8cm", luminophore=Lm_lr305, matrix=pmma, photocatalyst="MB",
                  photocatalyst_concentration=0.0012, solvent='ACN', tilt_LSC=True)

scene.add_objects(reactor.scene_obj)

lamp = LightSource(lamp_type='Sun')

lamp.set_lightsource(irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], lamp_wavelength = (300, 1100),
                     distance=1.25)
# lamp.set_lightsource(irradiated_area=(reactor.lsc.size[0], 0.15035), distance=0.025)
# lamp.move_lightsource(vector=(0, 0.01735))

trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100, use_visualiser=True,
                       show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
# set color on Trace.py while visualizing

# Run simulation

trace.start()

scene.stats.print_detailed()
text_head = str(scene.stats.print_excel_header() + "\n")
text = str(scene.stats.print_excel() + "\n")
write_me = open(file_path, 'a')
write_me.write(text_head)
write_me.write(text)
write_me.close()

sys.exit(0)

