from win32gui import *
import win32gui
import win32con
import sys,os
from time import sleep

from pvtrace.lscpm.SolarSimulators import *
from PIL import ImageGrab
import cv2
from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont



class PVTClose():

    def __init__(self, month, day, time):
        self.pict_gen_path = os.path.join(PVTDATA, "picture_video", str(month), str(day))
        self.save_pict_path = os.path.join(PVTDATA, "picture_video", str(month), str(day), str(time)+".jpeg")
        self.save_video_path = os.path.join(PVTDATA, "picture_video", "video")
        self.pict_time = time
        self.month = month
        self.day = day
        self.begin_circulation = True
        close_path = os.path.join(PVTDATA, 'automation_run', 'close_PVTrace.txt')
        self.config_file = open(close_path, "r")
        self.config_contents = self.config_file.readlines()

    def find_pvtrace_win(self, hwnd, mouse):
        global config_contents
        if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
            for content in self.config_contents:
                ads_info = []
                if not '|' in content :
                    continue
                else:
                    ads_info = content.split('|')
                if GetClassName(hwnd)==ads_info[0] and GetWindowText(hwnd)==ads_info[1]:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    self.begin_circulation = False

    def run_close(self):
        self.grab_picture()
        sleep(0.5)
        while self.begin_circulation:
            EnumWindows(self.find_pvtrace_win, 0)
            sleep(0.5)
        return self.save_pict_path

    def grab_picture(self, size=(10, 30, 970, 550)):
        file_gen_path = self.pict_gen_path
        file_path = self.save_pict_path
        hours = int(self.pict_time)
        minutes_cal = (self.pict_time - int(self.pict_time))*60
        if minutes_cal<10:
            minutes = '0{}'.format(int(round(minutes_cal)))
        elif int(round(minutes_cal))==60:
            minutes = '0{}'.format(0)
            hours += 1
        else:
            minutes = int(round(minutes_cal))
        Font4 = ImageFont.truetype("C:\Windows\Fonts/ariblk.ttf", 48)
        im = ImageGrab.grab(size)
        if not os.path.exists(file_gen_path):
            os.makedirs(file_gen_path)
        im.save(file_path, 'jpeg')
        iml = Image.open(file_path)
        draw = ImageDraw.Draw(iml)
        if self.month >= 3 and self.month <= 5:
            season = "spring"
        elif self.month >= 6 and self.month <= 8:
            season = "summer"
        elif self.month >= 9 and self.month <= 11:
            season = "autumn"
        else:
            season = "winter"
        draw.text((20, 20), season+ " " + str(self.day) +"/"+ str(self.month), (0, 0, 0), font=Font4)
        draw.text((20, 90), str(hours)+":"+str(minutes), (0, 0, 0), font=Font4)
        iml.save(file_path)

    # def make_vedio(self, fps=1, size=(960, 520)):
    #     fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    #     file_path = self.save_video_path
    #     if not os.path.exists(file_path):
    #         os.makedirs(file_path)
    #     videoWriter = cv2.VideoWriter(file_path, fourcc, fps, size)
    #     frame = cv2.imread(self.pict_gen_path + self.pict_time + '.jpeg')
    #     videoWriter.write(frame)
    #     videoWriter.release()

