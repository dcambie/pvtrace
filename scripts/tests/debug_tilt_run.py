# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.external.smarts.input_output import  *
from pvtrace.lscpm.SolarSimulators import *
from pvtrace.spencer import *


def broadband_irradiance(output_file_path):
    with open(output_file_path, 'r') as f:
        for line in f:
            if '  Direct Beam =  ' and 'Ground Reflected =' in line:
                list_find_line = line.split(' ')
                list_find_line = [x for x in list_find_line if x != '']
                tilted_irra_direct = float(list_find_line[3])
                tilted_irra_diffuse = float(list_find_line[7])
                return tilted_irra_direct, tilted_irra_diffuse

# set simulation time
year = 2017
month = 1
list_LSC_finish = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# set sunrise and sunset time in the day
list_start_time = [9, 8.5, 7.5, 6.5, 6, 5.5, 6, 6.5, 7.5, 8.5, 9, 9]
list_finish_time = [16.5, 17, 18, 18.5, 19.5, 19.5, 20, 19, 18, 17, 16, 16]

file_path = os.path.join(PVTDATA, 'radiance', '0406record.txt')
file_path_2 = os.path.join(PVTDATA, 'radiance', '0406recordpercent.txt')

# calculation begin
for mainloop_i in range(0, 12): #month
    month = mainloop_i + 1
    LSC_start_day = 1
    LSC_finish_day = list_LSC_finish[mainloop_i]

    while (LSC_start_day<=LSC_finish_day): # day
        LSC_begin_time = list_start_time[mainloop_i]
        LSC_finish_time = list_finish_time[mainloop_i]
        absorbed_total = 0 # the percentage of photon absorbed by channel; the default value is 0
        flag = 0 # count the number of simulation

        while (LSC_begin_time<=LSC_finish_time): # time

            # sun irradiance time of tilt LSC-PM is shorter than the horizontal LSC-PM
            try:
                tilt_angle = Tilt_solar_angle(year=year, month=month, day=LSC_start_day, standard_time=LSC_begin_time, standard_longitude=15,
                                              local_longitude=5.49, local_latitude=51.44, tilt_angle=28)
                tilt_angle.run_solar()
                x_i, y_i, z_i = tilt_angle.return_vector()

            except: # the sky is dark
                LSC_begin_time += 0.5
                continue

            spectrum_file = os.path.join(PVTDATA, 'autosmarts', 'spectput_file', str(year)+'_'+str(month)+'_'+str(LSC_start_day), str(LSC_begin_time),
                                         'smarts295.ext.txt')
            output_file = os.path.join(PVTDATA, 'autosmarts', 'output_file',
                                         str(year) + '_' + str(month) + '_' + str(LSC_start_day), str(LSC_begin_time),
                                         'smarts295.out.txt')

            tilted_irra_direct, tilted_irra_diffuse = broadband_irradiance(output_file)

            scene = pvtrace.Scene(level=logging.INFO, uuid='overwrite_me')
            logger = logging.getLogger('pvtrace')
            Lm_lr305 = LuminophoreMaterial('Limacryl_lr305', 1)  # red
            pmma = Matrix('PMMA')
            reactor = Reactor(reactor_name="47x47_chong_thickness0.8cm", luminophore=Lm_lr305, matrix=pmma,
                              photocatalyst="MB",
                              photocatalyst_concentration=0.0012, solvent='ACN')
            scene.add_objects(reactor.scene_obj)
            lamp = LightSource(lamp_type='SMARTSsolar_simulator', set_spectrumfile=spectrum_file)
            light_vector = (x_i, y_i, z_i)
            lampmove_vector = (-x_i * 0.225, -y_i * 0.225)
            lamp.set_lightsource(lamp_direction=light_vector,
                                 irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1],
                                 distance=0.225,
                                 smarts=True)
            lamp.move_lightsource(vector=lampmove_vector)
            trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=1000, use_visualiser=False,
                                   show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)

            trace.start()

            scene.stats.print_detailed()
            # get the absorption percentage from the database
            absorbed_channel = scene.stats.get_absorption()
            absorbed_total += absorbed_channel*tilted_irra_direct*0.47*0.47*0.1
            # prepare for next time simulation

            write_me = open(file_path_2, 'a')
            text = str(month) + '\t' + str(LSC_start_day) + '\t' + str(LSC_begin_time) + '\t' + str(absorbed_channel) + '\n'
            write_me.write(text)
            write_me.close()

            LSC_begin_time += 0.5

        # write average percent of absorption in the output txt on a daily basis
        write_me = open(file_path, 'a')
        text = str(month)+'\t'+str(LSC_start_day)+'\t'+str(absorbed_total)+'\n'
        write_me.write(text)
        write_me.close()
        # prepare for next day's simulation
        LSC_start_day += 16

# ATTENTION!!! Analysis.py has been changed to avoid bug
sys.exit(0)