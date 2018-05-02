import numpy as np
import os, sys
file_path = os.path.join('D:/', 'Fresnel', 'result.txt')

n1 = 1
n2 = 1.4859
text = ''

for theta1 in range(0, 91):
    text += str(theta1) + '\t'
    theta1 = theta1*np.pi/180
    theta2 = np.arcsin(n1*np.sin(theta1)/n2)
    Rs = ((n1*np.cos(theta1)-n2*np.cos(theta2))/(n1*np.cos(theta1)+n2*np.cos(theta2)))**2
    Rp = ((n1*np.cos(theta2)-n2*np.cos(theta1))/(n1*np.cos(theta2)+n2*np.cos(theta1)))**2
    Rlsc = (Rs + Rp)/2
    text += str(Rlsc) + '\n'

write_me = open(file_path, 'w')
write_me.write(text)
write_me.close()

sys.exit(0)