from __future__ import division
import os, ConfigParser

spacing = 1.0  # in mm
width = 0.35 * 8 + spacing * 9  # in mm

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (Fang bifurcation, 8 channels, '+str(spacing)+' mm spacing)')
config.set('Main', 'description', 'PDMS-based LSC-PM for scale-up, 8 channels '+str(spacing)+' mm spacing - Fang')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', str(width * 0.001))  # in m
config.set('LSC', 'length', '0.18505')  # in m
config.add_section('Channels')

geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z

x_start = width / 2 - (1.05/2)
geometry.append(((x_start, 0.000, 1), (1.05, 7.00, 1)))  # Inlet
geometry.append(((x_start, 178.05, 1), (1.05, 7.00, 1)))  # Outlet

x_start = 2.5 * spacing + 2 * 0.35 - 0.8
x_lenght = 4 * spacing + 4 * 0.35 + 1 * 1.6
geometry.append(((x_start, 7.000, 1), (x_lenght, 1.60, 1)))  # 1st bifurcation inlet
geometry.append(((x_start, 176.45, 1), (x_lenght, 1.60, 1)))  # 1st bifurcation outlet

geometry.append(((x_start, 8.600, 1), (1.60, 4.50, 1)))  # Left branch inlet
geometry.append(((x_start, 171.95, 1), (1.60, 4.50, 1)))  # Left branch outlet

x_start = width - x_start - 1.6
geometry.append(((x_start, 8.600, 1), (1.60, 4.50, 1)))  # Right branch inlet
geometry.append(((x_start, 171.95, 1), (1.60, 4.50, 1)))  # Right branch outlet

for n in range(1, 5):
    k = n * 2 - 1
    x_start2 = spacing * k + 0.35 * (k-1)  # get initial corresponding channel
    x_start2 += spacing/2 - 0.05  # (2*ch+spacing)/2 - width/2
    geometry.append(((x_start2, 13.90, 1), (0.8, 3.10, 1)))  # 2nd level branch, inlet
    geometry.append(((x_start2, 168.05, 1), (0.8, 3.10, 1)))  # 2nd level branch, outlet
    x_lenght = 2 * spacing + 2 * 0.35 + 0.8
    if n % 2 == 1:
        geometry.append(((x_start2, 13.10, 1), (x_lenght, 0.80, 1)))  # 2nd level bifurcation, inlet
        geometry.append(((x_start2, 171.15, 1), (x_lenght, 0.80, 1)))  # 2nd level bifurcation, outlet

for n in range(1, 9):
    x_start = spacing * n + 0.35 * (n-1)
    geometry.append(((x_start, 17.35, 1), (0.35, 150.35, 1)))  # n channel
    x_lenght = spacing + 0.35 * 2
    if n % 2 == 1:
        geometry.append(((x_start, 17.00, 1), (x_lenght, 0.35, 1)))  # 3rd level bifurcation, inlet
        geometry.append(((x_start, 167.7, 1), (x_lenght, 0.35, 1)))  # 3rd level bifurcation, outlet

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

channel = []
for i in range(0, len(geometry)):
    position = geometry[i]
    channel.append((position[0], position[1], 'box', 'Channel' + str(i)))

config.set('Channels', 'channels', str(channel))

# Writing our configuration file to 'example.cfg'
with open('Fang_8ch_'+str(spacing)+'mm.ini', 'wb') as configfile:
    config.write(configfile)
