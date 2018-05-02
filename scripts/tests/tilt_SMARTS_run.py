# -*- coding: utf-8 -*-

from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.external.smarts.input_output import  *
from pvtrace.lscpm.SolarSimulators import *

year = 2017
month = 1
list_LSC_finish = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
list_start_time = [9, 8.5, 7.5, 6.5, 6, 5.5, 6, 6.5, 7.5, 8.5, 9, 9]
list_finish_time = [16.5, 17, 18, 18.5, 19.5, 19.5, 20, 19, 18, 17, 16, 16]
a = 0
a_hor = 0
b = 0
b_hor = 0
flag = 1
file_path = os.path.join(PVTDATA, 'radiance', '22.txt')

for mainloop_i in range(0, 12):
    month = mainloop_i + 1
    LSC_start_day = 1
    LSC_finish_day = list_LSC_finish[mainloop_i]

    while (LSC_start_day<=LSC_finish_day):
        LSC_begin_time = list_start_time[mainloop_i]
        LSC_finish_time = list_finish_time[mainloop_i]
        while (LSC_begin_time<=LSC_finish_time):
            solar_angle = Smartangle(year=year, month=month, day=LSC_start_day, tilt_angle=42, time=LSC_begin_time)
            solar_angle.run_smarts()
            a += solar_angle.tilted_irra_direct*0.47*0.47*0.1 #0.47*0.47 is the surface area of LSC-PM; 0.1 is the time span unit:hour
            b += solar_angle.tilted_irra_diffuse*0.47*0.47*0.1
            LSC_begin_time += 0.1
            print(flag)
            flag += 1
        LSC_start_day += 1

    # print(a, a_hor, b, b_hor)
    text = str(a) + '\t' + str(b) + '\n'
    a=0
    b=0
    write_me = open(file_path, 'a')
    write_me.write(text)
    write_me.close()
