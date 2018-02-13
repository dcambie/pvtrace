import os, ConfigParser
import numpy as np

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Chong_red_20x20x0.3')
config.set('Main', 'description', '20x20cm square LSC with apt tubing PFA high purity'
                                  '(0.75 mm ID 1/16" OD) eight channels')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.2')
config.set('LSC', 'length', '0.2')
config.add_section('Channels')

# Simplified with axis and length in common among all the capillaries
chong_epi = 10**-6
default_od = 0.0015875
default_id = 0.00075
axis = 1
length = 0.2 - 2*chong_epi

geometry = []
#        ORIGIN:  X        Y     Z  AXIS LENGTH
geometry.append((12.5, chong_epi*1000, 1.5))  # Inlet
geometry.append((37.5, chong_epi*1000, 1.5))
geometry.append((62.5, chong_epi*1000, 1.5))
geometry.append((87.5, chong_epi*1000, 1.5))
geometry.append((112.5, chong_epi*1000, 1.5))
geometry.append((137.5, chong_epi*1000, 1.5))
geometry.append((162.5, chong_epi*1000, 1.5))
geometry.append((187.5, chong_epi*1000, 1.5))

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[coord * 0.001 for coord in capillary] for capillary in geometry]

capillary = []
for i in range(0, len(geometry)):
    position = geometry[i]

    # Origin, axis, length, OD, ID, name
    capillary.append(((position[0], position[1], position[2]), axis, length, default_od, default_id, 'Capillary' + str(i)))

config.set('Channels', 'capillaries', str(capillary))

# Writing our configuration file to 'example.cfg'
with open('20x20_chong_thickness0.3cm.ini', 'wb') as configfile:
    config.write(configfile)
