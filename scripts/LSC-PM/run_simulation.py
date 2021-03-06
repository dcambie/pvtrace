from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *

scene = pvtrace.Scene(level=logging.INFO, uuid="Fang_8ch_20mm_10k_hi")
logger = logging.getLogger('pvtrace')

# Create LSC-PM DYE material
lr305 = LuminophoreMaterial('Red305', 200)
# Create polymeric matrix
pdms = Matrix('pdms')

reactor = Reactor(reactor_name="Fang_8ch_20mm", luminophore=lr305, matrix=pdms, photocatalyst="MB",
                  photocatalyst_concentration=0.001, solvent='ACN')
scene.add_objects(reactor.scene_obj)

# lamp = LightSource(lamp_type='White LEDs')
# lamp.set_LED_voltage(voltage=8)
# lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)
lamp = LightSource(lamp_type='SolarSimulator')
lamp.set_lightsource(irradiated_area=(reactor.lsc.size[0], 0.15035), distance=0.025)
lamp.move_lightsource(vector=(0, 0.01735))


trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=10000, use_visualiser=False,
                       show_axis=True, show_counter=False, db_split=True, preserve_db_tables=True)
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
sys.exit(0)
