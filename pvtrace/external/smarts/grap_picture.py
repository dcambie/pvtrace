from PIL import ImageGrab

def grab_picture(size=None, file_path=None):
    im = ImageGrab.grab((10, 10, 460, 440))
    im.save('D:\PvTrace_git\pvtrace-fork\data/try.jpeg', 'jpeg')

if __name__ == '__main__':
    grab_picture()