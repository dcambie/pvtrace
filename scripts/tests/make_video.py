import PIL
import os
import cv2



from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont

times = ["5 AM", "5.30 AM", "6 AM", "6.30 AM", "7 AM", "7.30 AM", "8 AM", "8.30 AM", "9 AM", "9.30 AM", "10 AM", "10.30 AM",
         "11 AM", "11.30 AM", "12 PM", "12.30 PM"]
texts = ['8.09%', '7.26%', '7.57%', '7.81%', '7.92%', '8.08%', '8.20%', '8.40%', '8.33%', '8.46%', '8.49%', '8.42%', '8.44%',
         '8.33%', '8.47%', '8.49%']

for i in range(0, 16):

    mainloop_i = 5.0 + i*0.5
    Font4 = ImageFont.truetype("C:\Windows\Fonts/ariblk.ttf", 48)

    iml = Image.open('C:/Users/qwt/Desktop/'+str(mainloop_i)+'.jpg')
    draw = ImageDraw.Draw(iml)
    draw.text((20, 40), times[i], (0, 0, 0), font=Font4)
    draw.text((20, 100), texts[i], (0, 0, 0), font=Font4)
    iml2 = iml.crop((10, 35, 976, 640))
    iml2.save('C:/Users/qwt/Desktop/picture/'+str(mainloop_i)+'.jpg')

fps = 1

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
videoWriter = cv2.VideoWriter('C:/Users/qwt/Desktop/saveVideo.avi',fourcc,fps,(966,605))

for i in range(0, 16):
    mainloop_i = 5.0 + i*0.5
    frame = cv2.imread('C:/Users/qwt/Desktop/picture/'+str(mainloop_i)+'.jpg')
    videoWriter.write(frame)
videoWriter.release()
