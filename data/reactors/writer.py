import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (Fang, 16 channels, 0.35 mm nozzle)')
config.set('Main', 'description', 'PDMS-based LSC-PM 5x5cm 16 channels Fang')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.05')
config.set('LSC', 'length', '0.05')
config.add_section('Channels')


geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z
geometry.append(((4.975, 0.000, 1), (1.05, 10.00, 1)))  # Inlet, bigger for the first 10 mm
geometry.append(((5.325, 10.00, 1), (0.35, 37.675, 1)))  # 1st channel top

geometry.append(((5.675, 47.325, 1), (2.25, 0.35, 1)))  # 1st connection
geometry.append(((7.925, 9.825, 1), (0.35, 37.85, 1)))  # 2nd channel (shorter!)
geometry.append(((8.275, 9.825, 1), (2.25, 0.35, 1)))  # 2nd connection *
geometry.append(((10.525, 9.825, 1), (0.35, 37.85, 1)))  # 3rd channel
geometry.append(((10.875, 47.325, 1), (2.25, 0.35, 1)))  # 3rd connection
geometry.append(((13.125, 2.325, 1), (0.35, 45.35, 1)))  # 4th channel
geometry.append(((13.475, 2.325, 1), (2.25, 0.35, 1)))  # 4th connection
geometry.append(((15.725, 2.325, 1), (0.35, 45.35, 1)))  # 5th channel
geometry.append(((16.075, 47.325, 1), (2.25, 0.35, 1)))  # 5th connection
geometry.append(((18.325, 2.325, 1), (0.35, 45.35, 1)))  # 6th channel
geometry.append(((18.675, 2.325, 1), (2.25, 0.35, 1)))  # 6th connection
geometry.append(((20.925, 2.325, 1), (0.35, 45.35, 1)))  # 7th channel
geometry.append(((21.275, 47.325, 1), (2.25, 0.35, 1)))  # 7th connection
geometry.append(((23.525, 2.325, 1), (0.35, 45.35, 1)))  # 8th channel
geometry.append(((23.875, 2.325, 1), (2.25, 0.35, 1)))  # 8th connection
geometry.append(((26.125, 2.325, 1), (0.35, 45.35, 1)))  # 9th channel
geometry.append(((26.475, 47.325, 1), (2.25, 0.35, 1)))  # 9th connection
geometry.append(((28.725, 2.325, 1), (0.35, 45.35, 1)))  # 10th channel
geometry.append(((29.075, 2.325, 1), (2.25, 0.35, 1)))  # 10th connection
geometry.append(((31.325, 2.325, 1), (0.35, 45.35, 1)))  # 11th channel
geometry.append(((31.675, 47.325, 1), (2.25, 0.35, 1)))  # 11th connection
geometry.append(((33.925, 2.325, 1), (0.35, 45.35, 1)))  # 12th channel
geometry.append(((34.275, 2.325, 1), (2.25, 0.35, 1)))  # 12th connection
geometry.append(((36.525, 2.325, 1), (0.35, 45.35, 1)))  # 13th channel
geometry.append(((36.875, 47.325, 1), (2.25, 0.35, 1)))  # 13th connection
geometry.append(((39.125, 9.825, 1), (0.35, 37.85, 1)))  # 14th channel
geometry.append(((39.475, 9.825, 1), (2.25, 0.35, 1)))  # 14th connection
geometry.append(((41.725, 9.825, 1), (0.35, 37.85, 1)))  # 15th channel
geometry.append(((42.075, 47.325, 1), (2.25, 0.35, 1)))  # 15th connection

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
with open('5x5_fang_16ch.ini', 'wb') as configfile:
    config.write(configfile)
