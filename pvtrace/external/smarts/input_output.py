import os, sys
import shutil
import numpy as np
from pvtrace import PVTSMART, PVTDATA
import pvtrace.external as pve


class Smartangle():
    def __init__(self, year=2017, month=6, day=21, time=7, tilt_angle=28, longitude=5.49, latitude=51.44):
        self.exe_path = PVTSMART
        self.year = year
        self.month = month
        self.day = day
        self.time = time
        self.date = [year, ' ', month, ' ', day, ' ', time]
        self.tilt_angle = tilt_angle
        self.input_file_path = os.path.join(PVTSMART, 'smarts295.inp.txt')
        self.output_file_path = os.path.join(PVTSMART, 'smarts295.out.txt')
        self.spectra_file_path = os.path.join(PVTSMART, 'smarts295.ext.txt')
        self.longitude = longitude
        self.latitude = latitude
        self.zenith_angle = 0
        self.azimuth_angle = 0
        self.out_spectra_file_path = ""

    def write_input(self):
        file_path = os.path.join(PVTSMART, 'smarts295.inp.txt')
        text = ''
        comments = "'Simulation for" +str(self.day) + '/' + str(self.month) +" ' \n"
        NON_CHANGE = "1\n1013.25 0 0\n1\n'MLS'\n1\n1\n1\n400\n1\n'S&F_URBAN'\n0\n.084\n-1\n0\n1\n"
        tilt_angle = "-1 " + str(self.tilt_angle) + " 180\n"
        NON_CHANGE2 = "0\n350 700 1.0 1366.1\n2\n350 700 1\n6\n3 4 5 6 7 8\n1\n0 2.9 0\n0\n0\n0\n3\n"
        date_str = [str(i) for i in self.date]
        date = "".join(date_str)
        DAY_HOUR_EIN = date + ' ' + str(self.latitude) + ' ' + str(self.longitude) + ' 1\n'
        # DAY_HOUR_EIN = '2017 6 21 5.5 51.44 5.49 1\n'
        text += comments
        text += NON_CHANGE
        text += tilt_angle
        text += NON_CHANGE2
        text += DAY_HOUR_EIN
        write_me = open(file_path, 'w')
        write_me.write(text)
        write_me.close()

    def run_smarts(self):
        self.write_input()
        os.chdir(self.exe_path)
        exe_batch_path = os.path.join(self.exe_path, 'smarts295bat.exe')
        os.system(exe_batch_path)
        self.find_angle()
        self.broadband_irradiance()
        self.copy_txt()
        vx, vy, vz = self.return_solarposition()
        self.delete_txt()
        return vx, vy, vz

    def copy_txt(self):
        save_input_file = os.path.join('D:/', 'autosmarts', str(self.tilt_angle), 'input_file', str(self.year)+"_"+str(self.month)+"_"+str(self.day), str(self.time))
        save_output_file = os.path.join('D:/', 'autosmarts', str(self.tilt_angle), 'output_file', str(self.year) + "_" + str(self.month) + "_" + str(self.day), str(self.time))
        save_spect_file = os.path.join('D:/', 'autosmarts', str(self.tilt_angle), 'spectput_file', str(self.year) + "_" + str(self.month) + "_" + str(self.day), str(self.time))
        if not os.path.exists(save_input_file):
            os.makedirs(save_input_file)
            shutil.move('smarts295.inp.txt', save_input_file)
        if not os.path.exists(save_output_file):
            os.makedirs(save_output_file)
            shutil.move('smarts295.out.txt', save_output_file)
        if not os.path.exists(save_spect_file):
            os.makedirs(save_spect_file)
            shutil.move('smarts295.ext.txt', save_spect_file)
        self.out_spectra_file_path = os.path.join(save_spect_file, "smarts295.ext.txt")


    def delete_txt(self):
        # smarts would have mistakes if output file exists
        if os.path.isfile(self.output_file_path):
            os.remove(self.output_file_path)
        if os.path.isfile(self.spectra_file_path):
            os.remove(self.spectra_file_path)

    def find_angle(self):
        with open(self.output_file_path, "r") as f:
            for line in f:
                if 'Zenith Angle (apparent) = ' in line:
                    find_line = line.strip('\n')
                    list_find_line = find_line.split(' ')
                    zenith_angle_str = list_find_line[8]
                    azimuth_angle_str = list_find_line[-1]
                    self.zenith_angle = float(zenith_angle_str)/180*np.pi
                    self.azimuth_angle = float(azimuth_angle_str)/180*np.pi

    def broadband_irradiance(self):
        with open(self.output_file_path, 'r') as f:
            for line in f:
                if '  Direct Beam =  ' and ' Clearness index, KT =' in line:
                    list_find_line = line.split(' ')
                    list_find_line = [x for x in list_find_line if x != '']
                    self.horizon_irra_direct = float(list_find_line[3])
                    self.horizon_irra_diffuse = float(list_find_line[6])
                if '  Direct Beam =  ' and 'Ground Reflected =' in line:
                    list_find_line = line.split(' ')
                    list_find_line = [x for x in list_find_line if x != '']
                    self.tilted_irra_direct = float(list_find_line[3])
                    self.tilted_irra_diffuse = float(list_find_line[7])

    def return_solarposition(self):
        vector_x = np.tan(self.zenith_angle)*np.sin(self.azimuth_angle)
        vector_y = -np.tan(self.zenith_angle)*np.cos(self.azimuth_angle)
        vector_z = -1
        return vector_x, vector_y, vector_z


                    # os.chdir("D:\PvTrace_git\pvtrace-fork\SMARTS_295_PC")
    # file_path = os.path.join('D:/', 'PvTrace_git', 'pvtrace-fork', 'SMARTS_295_PC', 'smarts295.inp.txt')
    # text = ''
    # angle = 28
    # comments = "'Chong_first_Time'\n"
    #
    # NON_CHANGE = "1\n1013.25 0 0\n1\n'MLS'\n1\n1\n1\n400\n1\n'S&F_URBAN'\n0\n.084\n-1\n0\n1\n"
    #
    # tilt_angle = "-1 "+ str(angle) + " 0\n"
    #
    # NON_CHANGE2 = "0\n350 700 1.0 1366.1\n2\n350 700 1\n2\n3 5\n1\n0 2.9 0\n0\n0\n0\n3\n"
    #
    # DAY_HOUR_EIN = '2017 6 21 5.5 51.44 5.49 1\n'
    # text += comments
    # text += NON_CHANGE
    # text += tilt_angle
    # text += NON_CHANGE2
    # text += DAY_HOUR_EIN
    # write_me = open(file_path, 'w')
    # write_me.write(text)
    # write_me.close()
    #
    # os.system('D:\PvTrace_git\pvtrace-fork\SMARTS_295_PC\smarts295bat.exe')
    # copy_txt()
    #
    # sys.exit(0)
if __name__ == '__main__':
    a = Smartangle()
    a.run_smarts()
    print(a.tilted_irra_diffuse)
