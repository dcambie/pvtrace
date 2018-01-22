from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
from pvtrace.external import povexport

scene = pvtrace.Scene(level=logging.INFO, uuid=None)
logger = logging.getLogger('pvtrace')

# Create LSC-PM DYE material
lr305 = LuminophoreMaterial('Red305', 200)
# Create polymeric matrix
pdms = Matrix('pdms')

reactors = ('Fang_8ch_0.5mm',
            'Fang_8ch_1.0mm',
            'Fang_8ch_2mm',
            'Fang_8ch_3mm',
            'Fang_8ch_4mm',
            'Fang_8ch_5mm',
            'Fang_8ch_6mm',
            'Fang_8ch_7mm',
            'Fang_8ch_8mm',
            'Fang_8ch_9mm',
            'Fang_8ch_10mm',
            'Fang_8ch_chamber_0.5mm',
            'Fang_8ch_chamber_1mm',
            'Fang_8ch_chamber_2mm',
            'Fang_8ch_chamber_3mm',
            'Fang_8ch_chamber_4mm',
            'Fang_8ch_chamber_5mm',
            'Fang_8ch_chamber_6mm',
            'Fang_8ch_chamber_7mm',
            'Fang_8ch_chamber_8mm',
            'Fang_8ch_chamber_9mm',
            'Fang_8ch_chamber_10mm')

rea = []
for reactor in reactors:
    rea.append(Reactor(reactor_name=reactor, luminophore=lr305, matrix=pdms, photocatalyst="MB", solvent="Air"))

all_obj = []
count = 0
n = 0
xspacing = 0
yspacing = 0
for reactor_obj in rea:
    n += 1
    xspacing += reactor_obj.lsc.size[0] + 0.005
    if n == 12:
        xspacing = 0.005 + reactor_obj.lsc.size[0]
        yspacing = 0.2
    for obj in reactor_obj.scene_obj:
        obj.shape.append_transform(tf.translation_matrix((xspacing, yspacing, 0)))
        obj.name = str(count)+'_' + obj.name
        all_obj.append(obj)
    count += 1

scene.add_objects(all_obj)

lamp = LightSource(lamp_type='SolarSimulator')
lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)

trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=0, use_visualiser=True,
                       show_axis=True, show_counter=False, db_split=True, preserve_db_tables=True)

#scene.pov_render(camera_position=(1.6, 0, 2), camera_target=(1.6, 1.39, 0), height=320, width=640)


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

# scene.stats.print_detailed()
# scene.stats.create_graphs()

sys.exit(0)
