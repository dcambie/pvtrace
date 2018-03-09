import numpy as np
import os
from pvtrace import *
from pvtrace.Analysis import xyplot
import math
filename = os.path.join(PVTDATA, 'smarts', 'jun21.txt')
LIMIT = 352
file_count = 5.0
url_list = []
with open(filename) as f:
    for line in f:
        url_list.append(line)
        if len(url_list) < LIMIT:
            continue
        file_name='D:/test/june21_'+str(file_count)+'hr.txt'
        with open(file_name, 'w') as file:
            for url in url_list[:-1]:
                file.write(url)
            file.write(url_list[-1].strip())
            url_list=[]
            file_count+=0.5
print('done')

'''

data = np.loadtxt(filename, skiprows=[1, 5])
x = np.array(data[32, 0], dtype=np.float32)
y = np.array(data[32, 1], dtype=np.float32)
print(x, y)

for mainloop_i in range(0, 14):
    x = np.array(data[:352:1, 0], dtype=np.float32)
    y = np.array(data[:352:1, 0], dtype=np.float32)
'''