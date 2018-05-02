import pvtrace.external.smarts.input_output as inout
import sys, os

debug = inout.Smartangle()
a, b, c= debug.run_smarts()
print(a, b, c)
sys.exit(0)
#
# with open('D:\PvTrace_git\pvtrace-fork\data\\autosmarts\output_file\\2017_6_21\\5.5\smarts295.out.txt', "r") as f:
#     for line in f:
#         if 'Zenith Angle (apparent) = ' in line:
#             find_line = line.strip('\n')
#             list_find_line = find_line.split(' ')
#             zenith_angle_str = list_find_line[8]
#             azimuth_angle_str = list_find_line[-1]
#             zenith_angle = float(zenith_angle_str)
#             azimuth_angle = float(azimuth_angle_str)
#             print(zenith_angle, azimuth_angle)
