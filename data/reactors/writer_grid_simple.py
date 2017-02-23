from __future__ import division
import os, ConfigParser
from math import pow

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (1 sq. m  10 cm spacing, grid w/ borders)')
config.set('Main', 'description', '1x1m reactor with 500um channels full-width grid every 10 cm + borders')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.add_section('Channels')

epsilon = pow(10, -6)
width = 0.5
spacing = 100
num = 10
halfwidth = width/2
side = num * spacing

config.set('LSC', 'width', str((side+2*epsilon)/1000))
config.set('LSC', 'length', str((side+2*epsilon)/1000))


geometry = []
for x in range(1, num):
    #        ORIGIN:  X        Y     Z  L:   X      Y   Z
    geometry.append(((x*spacing-halfwidth, 0.000, epsilon), (width, side, 3-2*epsilon)))  # Vertical channels

# Borders
geometry.append(((0, 0.000, epsilon), (width, side, 3-2*epsilon)))               # Vertical
geometry.append(((side-width, 0.000, epsilon), (width, side, 3-2*epsilon)))      # Vertical

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

channel = []
for i in range(0, len(geometry)):
    position = geometry[i]
    channel.append((position[0], position[1], 'box', 'Channel' + str(i)))

config.set('Channels', 'channels', str(channel))

# Writing our configuration file to 'example.cfg'
with open('1sqm_10cm_borders.ini', 'wb') as configfile:
    config.write(configfile)
