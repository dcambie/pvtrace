# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.external.smarts.input_output import  *
from pvtrace.lscpm.SolarSimulators import *
from pvtrace.AutomaticVedio import *

year = 2017
month = 12
day = 22
LSC_start_time = 9
LSC_finish_time = 15

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
video_file_path = os.path.join(PVTDATA, "picture_video", "video")
if not os.path.exists(video_file_path):
    os.makedirs(video_file_path)
video_file_path_avi = os.path.join(PVTDATA, "picture_video", "video", str(month)+'_'+str(day)+'.avi')
videoWriter = cv2.VideoWriter(video_file_path_avi, fourcc, 1, (960, 520))

while (LSC_start_time<LSC_finish_time):
#1 Create LSC-PM DYE material and host material

    Lm_lr305 = LuminophoreMaterial('Limacryl_lr305', 1)#red
    pmma = Matrix('PMMA')

    scene = pvtrace.Scene(level=logging.INFO, uuid="overwrite_me")
    logger = logging.getLogger('pvtrace')
    # change the view in Visualizer.py
    reactor = Reactor(reactor_name="47x47_chong_thickness0.8cm", luminophore=Lm_lr305, matrix=pmma, photocatalyst="MB",
                      photocatalyst_concentration=0.0012, solvent='ACN')
    scene.add_objects(reactor.scene_obj)

    # set solar angle and irradiance spectra
    solar_angle = Smartangle(year=year, month=month, day=day, time=LSC_start_time)
    x_i, y_i, z_i = solar_angle.run_smarts()
    spectrum_file = solar_angle.out_spectra_file_path

    lamp = LightSource(lamp_type='SMARTSsolar_simulator', set_spectrumfile = spectrum_file)
    light_vector = (x_i, y_i, z_i)
    lampmove_vector = (-x_i*0.125, -y_i*0.125)
    # tilted spectrum data should be involved by changing the class spectrum
    lamp.set_lightsource(lamp_direction=light_vector,
                         irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.125, smarts=True)
    lamp.move_lightsource(vector=lampmove_vector)

    trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=100, use_visualiser=True,
                           show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
    # set color on Trace.py while visualizing

    # Run simulation

    trace.start()

    close_me = PVTClose(month=month, day=day, time=LSC_start_time)
    pict_path = close_me.run_close()
    frame = cv2.imread(pict_path)
    videoWriter.write(frame)
    LSC_start_time += 0.1

videoWriter.release()
sys.exit(0)

