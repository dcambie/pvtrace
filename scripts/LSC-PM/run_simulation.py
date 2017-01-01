from pvtrace import *
from pvtrace.lscpm.Reactor import Reactor

scene = pvtrace.Scene()
logger = logging.getLogger('pvtrace')

reactor = Reactor(reactor_name="5x5_6ch_squared", dye="Red305", dye_concentration=0.20, photocatalyst="MB",
                  photocatalyst_concentration=0.0004)
scene.add_objects(reactor.scene_obj)

lamp = LightSource(lamp_type='SolarSimulator', irradiated_area=(0.05, 0.05), distance=0.025)
trace = pvtrace.Tracer(scene=scene, source=lamp.source, seed=None, throws=100, use_visualiser=True,
                       show_axis=True, show_counter=False, db_split=True, preserve_db_tables=True)
trace.show_lines = True
trace.show_path = False

# Run simulation
tic = time.clock()
logger.info('Simulation Started (time: ' + str(tic) + ')')
trace.start()
toc = time.clock()
logger.info('Simulation Ended (time: ' + str(toc) + ', elapsed: ' + str(toc - tic) + ' s)')

# for obj in scene.objects:
#     if type(obj) is pvtrace.Devices.LSC:
#         print("lsc losses")
#         lsc_loss = obj.loss()
#         print(lsc_loss)
#         logger.info("LSC losses are "+str(lsc_loss)+" photons")
#         lsc_loss_reabs = obj.loss_reabs()
#         print(lsc_loss_reabs)
#         lsc_reabs = obj.reabs()
#         print(lsc_reabs)
#
#         surfaces = ('far', 'near', 'right', 'left', 'top', 'bottom')
#         for face in surfaces:
#             face_photons = obj.count_face(face_name=face)
#             logger.info("in face "+face+" there are "+str(face_photons)+" photons")
#
#         obj.print_store()
# spectrum = obj.spectrum_face(surface_names=('far', 'near', 'right', 'left'))
# print(spectrum)
# For reproducibility reasons always append git version to results (tested on linux only)
label = subprocess.check_output(["git", "describe"], cwd=PVTDATA, shell=True)
logger.info('PvTrace ' + str(label) + ' simulation ended')

print(scene.stats.print_excel_header() + "\n")
print(scene.stats.print_excel() + "\n")

# scene.stats.print_detailed()
# scene.stats.create_graphs()

# plane = pvtrace.Geometry.Plane()
# plane.name = 'base for render'
# scene.add_object(plane)
# scene.pov_render(camera_position=(-0.05, 0.025, 0.05), camera_target=(0.025, 0.025, 0), height=1080, width=1920)
# stats.history()
# stats.save_db()



sys.exit(0)