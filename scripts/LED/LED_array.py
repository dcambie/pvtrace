from __future__ import division, print_function
from pvtrace import *
import numpy as np

photons_per_led = 100

scene = pvtrace.Scene('overwrite_me')
logger = logging.getLogger('pvtrace')
logger.info('Starting LED_array simulation')

logger.info("Creating Light source objects")
led = []
led.append(PointSource(spectrum=None, wavelength=555, center=(0., 0., 0.5,), phi_min=0, phi_max=2 * np.pi, theta_min=0,
                       theta_max=np.pi))

detection_plane = SimpleCell(FinitePlane(length=1, width=1), origin=(-0.5, -0.5, 0.))
scene.add_object(detection_plane)

for source in led:
    trace = pvtrace.Tracer(scene=scene, source=source, seed=None, throws=photons_per_led, use_visualiser=True,
                           show_log=False, show_axis=True, show_counter=False, db_split=True)
    # Run simulation
    tic = time.clock()
    logger.info('Simulation Started (time: ' + str(tic) + ')')
    trace.start()
    toc = time.clock()
    logger.info('Simulation Ended (time: ' + str(toc) + ', elapsed: ' + str(toc - tic) + ' s)')

label = subprocess.check_output(["git", "describe"], cwd=PVTDATA, shell=True)
logger.info('PvTrace ' + label + ' simulation ended')

detection_plane.print_store()

sys.exit(0)
