import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (Fang, 2 channels, 0.35 mm nozzle)')
config.set('Main', 'description', 'PDMS-based LSC-PM 5x5cm 2 channels Fang')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.05')
config.set('LSC', 'length', '0.05')
config.add_section('Channels')


geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z
geometry.append(((4.975, 0.000, 1), (1.05, 10.00, 1)))  # Inlet, bigger for the first 10 mm
geometry.append(((5.325, 10.00, 1), (0.35, 37.675, 1)))  # 1st channel top

geometry.append(((5.675, 47.325, 1), (38.65, 0.35, 1)))  # connection


geometry.append(((44.325, 10.000, 1), (0.35, 37.675, 1)))  # last channel bottom
geometry.append(((43.975,  0.000, 1), (1.05, 10.00, 1)))  # Outlet, bigger for the first 10 mm

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

channel = []
for i in range(0, len(geometry)):
    position = geometry[i]
    channel.append((position[0], position[1], 'box', 'Channel' + str(i)))

config.set('Channels', 'channels', str(channel))

# Writing our configuration file to 'example.cfg'
with open('5x5_fang_2ch.ini', 'wb') as configfile:
    config.write(configfile)
