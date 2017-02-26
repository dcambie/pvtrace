from __future__ import division
import os, ConfigParser
from math import pow

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (1 sq. m  2.5 cm spacing, grid 1 direction w/ borders)')
config.set('Main', 'description', '1x1m reactor, 500um channels full-width grid in 1 direction every 2.5 cm + borders')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.add_section('Channels')

epsilon = pow(10, -6)
width = 0.5
spacing = 25
num = 40
halfwidth = width/2
side = num * spacing

config.set('LSC', 'width', str(side/1000))
config.set('LSC', 'length', str(side/1000))

geometry = []
for x in range(0, num):
    # This creates vertical (y-long) channels from 0+num*spacing to start+width
    geometry.append(((x*spacing, 0.000, epsilon), (width, side, 3-2*epsilon)))  # Vertical channels
    for y in range(0, num):
        # This makes the horizontal (x-long) pieces to complete the grid
        # per each x:
        geometry.append(((x*spacing+width, y*spacing, epsilon), (spacing-width, width, 3 - 2 * epsilon)))
    # Last horizontal piece in the right position note the additional "-width" in Y-origin to prevent misplacement
    geometry.append(((x * spacing + width, num * spacing-width, epsilon), (spacing - width, width, 3 - 2 * epsilon)))

geometry.append(((num * spacing-width, 0.000, epsilon), (width, side, 3 - 2 * epsilon)))  # Vertical channels

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

channel = []
for i in range(0, len(geometry)):
    position = geometry[i]
    channel.append((position[0], position[1], 'box', 'Channel' + str(i)))

config.set('Channels', 'channels', str(channel))

# Writing our configuration file to 'example.cfg'
with open('1sqm_2dir_2.5cm.ini', 'wb') as configfile:
    config.write(configfile)
