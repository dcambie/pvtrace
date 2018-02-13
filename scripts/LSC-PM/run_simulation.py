# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
# blue red thickness: 3mm green: 4mm
# blue not yet, green EY, red Methylene Blue,
# set episilon to prevent the possibility of matching fate and generate


# scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_rebuttal2_6")
scene = pvtrace.Scene(level=logging.INFO, uuid="overwrite_me")
logger = logging.getLogger('pvtrace')

# Create LSC-PM DYE material
lr305 = LuminophoreMaterial('Red305', 200)#red
k160 = LuminophoreMaterial('K160', 1)#green
blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)#blue
# Create polymeric matrix
pdms = Matrix('pdms')
pmma = Matrix('PMMA')

reactor = Reactor(reactor_name="chong_red_10x10x0.3cm", luminophore=lr305, matrix=pmma, photocatalyst="MB",
                  photocatalyst_concentration=0.004, solvent='ACN')
scene.add_objects(reactor.scene_obj)

# lamp = LightSource(lamp_type='White LEDs')
# lamp.set_LED_voltage(voltage=8)
# lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)
lamp = LightSource(lamp_type='SolarSimulator')
# fixed by chong in order to run the different reactor without altering the scripts
lamp.set_lightsource(irradiated_length=reactor.lsc_length, irradiated_width=reactor.lsc_width, distance=0.025)
# lamp.set_lightsource(irradiated_area=(reactor.lsc.size[0], 0.15035), distance=0.025)
# lamp.move_lightsource(vector=(0, 0.01735))

trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100, use_visualiser=True,
                       show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
# set color on Trace.py while visualizing

# Run simulation
tic = time.clock()
logger.info('Simulation Started (time: ' + str(tic) + ')')
trace.start()
toc = time.clock()
logger.info('Simulation Ended (time: ' + str(toc) + ', elapsed: ' + str(toc - tic) + ' s)')

label = subprocess.check_output(["git", "describe", "--always"], cwd=PVTDATA, shell=True)
logger.info('PvTrace ' + str(label) + ' simulation ended')

print(scene.stats.print_excel_header() + "\n")
print(scene.stats.print_excel() + "\n")

# keys = scene.stats.db.objects_with_records()
# print(keys)
# channels_with_photons = []
# max = 0
# for solid_object in keys:
#     if solid_object.startswith("Channel"):
#         channels_with_photons.append(solid_object)

photons_in_object = {}
photonsum = 0
for obj in scene.objects:
    if type(obj) is pvtrace.Devices.Channel and len(obj.store)>0:
        photon_loss = len(obj.store['loss'])
        photons_in_object[obj.name] = photon_loss

logger.info("Photons in channels: "+str(photons_in_object))

print("Channel No, Photons")
for entry, value in photons_in_object.items():
    print(str(entry)[7:]+", "+str(value))

scene.stats.create_graphs()

toc2 = time.clock()
t_span = toc2-tic
# print(photons_in_object)
print("it takes %0.1f secs to complete the whole simulation" % t_span)
# print("sum is "+str(photonsum))

sys.exit(0)
