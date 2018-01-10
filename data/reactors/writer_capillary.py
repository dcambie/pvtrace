import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'LSC-PM PMMA+PFA Reactor single channel')
config.set('Main', 'description', 'Evonik-type 5x5cm square LSC with apt tubing PFA high purity'
                                  '(0.75 mm ID 1/16" OD) single channel in the center')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.005')
config.set('LSC', 'length', '0.05')
config.add_section('Channels')

# Simplified with axis and length in common among all the capillaries
default_od = 0.0015875
default_id = 0.00075
axis = 1
length = 0.05

geometry = []
#        ORIGIN:  X        Y     Z  AXIS LENGTH
geometry.append((2.5, 0, 1.5))  # Inlet

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[coord * 0.001 for coord in capillary] for capillary in geometry]

capillary = []
for i in range(0, len(geometry)):
    position = geometry[i]

    # Origin, axis, length, OD, ID, name
    capillary.append(((position[0], position[1], position[2]), axis, length, default_od, default_id, 'Capillary' + str(i)))

config.set('Channels', 'capillaries', str(capillary))

# Writing our configuration file to 'example.cfg'
with open('LSC-PM_PMMA_PFA_750_single_5x1cm.ini', 'wb') as configfile:
    config.write(configfile)
