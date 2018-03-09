from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
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

reactor = Reactor(reactor_name="10x10_chong_thickness0.3cm", luminophore=lr305, matrix=pmma, photocatalyst="MB",
                  photocatalyst_concentration=0.004, solvent='ACN')
scene.add_objects(reactor.scene_obj)

lamp = LightSource(lamp_type='SolarSimulator')

lamp.set_lightsource(lamp_direction=(-4.235, -1.743, -1),
                     irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.025)
lamp.move_lightsource(vector=(4.235*0.025, 1.743*0.025))

for x, y in zip(lamp.spectrum.x, lamp.spectrum.y):
    print(x, y)



