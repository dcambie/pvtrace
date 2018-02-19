import os, ConfigParser
import numpy as np

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', '20x20_chong_thickness0.3cm_WE')
config.set('Main', 'description', '20x20cm square LSC with apt tubing PFA high purity'
                                  '(0.75 mm ID 1/16" OD) eight channels')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.1')
config.set('LSC', 'length', '0.1')
config.add_section('Channels')

# Simplified with axis and length in common among all the capillaries
chong_epi = 10**-6
default_od = 0.0015875
default_id = 0.00075
axis = 0
length = 0.1 - 2*chong_epi

geometry = []
#        ORIGIN:  X        Y     Z  AXIS LENGTH
geometry.append((chong_epi*1000, 12.5, 1.5))  # Inlet
geometry.append((chong_epi*1000, 37.5, 1.5))
geometry.append((chong_epi*1000, 62.5, 1.5))
geometry.append((chong_epi*1000, 87.5, 1.5))

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[coord * 0.001 for coord in capillary] for capillary in geometry]

capillary = []
for i in range(0, len(geometry)):
    position = geometry[i]

    # Origin, axis, length, OD, ID, name
    capillary.append(((position[0], position[1], position[2]), axis, length, default_od, default_id, 'Capillary' + str(i)))

config.set('Channels', 'capillaries', str(capillary))

# Writing our configuration file to 'example.cfg'
with open('10x10_chong_thickness0.3cm_WE.ini', 'wb') as configfile:
    config.write(configfile)
