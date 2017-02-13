import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (Fang, 20 channels, 0.35 mm nozzle)')
config.set('Main', 'description', 'PDMS-based LSC-PM 5x5cm 20 channels Fang')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.05')
config.set('LSC', 'length', '0.05')
config.add_section('Channels')


geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z
geometry.append(((4.975, 0.000, 1), (1.05, 10.00, 1)))  # Inlet, bigger for the first 10 mm
geometry.append(((5.325, 10.00, 1), (0.35, 37.675, 1)))  # 1st channel top

geometry.append(((5.675, 47.325, 1), (1.703, 0.35, 1)))  # 1st connection
geometry.append(((7.378, 9.825, 1), (0.35, 37.85, 1)))  # 2nd channel (shorter!)
geometry.append(((7.728, 9.825, 1), (1.702, 0.35, 1)))  # 2nd connection
geometry.append(((9.430, 9.825, 1), (0.35, 37.85, 1)))  # 3rd channel
geometry.append(((9.780, 47.325, 1), (1.703, 0.35, 1)))  # 3rd connection
geometry.append(((11.483, 2.325, 1), (0.35, 45.35, 1)))  # 4th channel
geometry.append(((11.833, 2.325, 1), (1.703, 0.35, 1)))  # 4th connection
geometry.append(((13.536, 2.325, 1), (0.35, 45.35, 1)))  # 5th channel
geometry.append(((13.886, 47.325, 1), (1.702, 0.35, 1)))  # 5th connection
geometry.append(((15.588, 2.325, 1), (0.35, 45.35, 1)))  # 6th channel
geometry.append(((15.938, 2.325, 1), (1.703, 0.35, 1)))  # 6th connection
geometry.append(((17.641, 2.325, 1), (0.35, 45.35, 1)))  # 7th channel
geometry.append(((17.991, 47.325, 1), (1.702, 0.35, 1)))  # 7th connection
geometry.append(((19.693, 2.325, 1), (0.35, 45.35, 1)))  # 8th channel
geometry.append(((20.043, 2.325, 1), (1.703, 0.35, 1)))  # 8th connection
geometry.append(((21.746, 2.325, 1), (0.35, 45.35, 1)))  # 9th channel
geometry.append(((22.096, 47.325, 1), (1.703, 0.35, 1)))  # 9th connection
geometry.append(((23.799, 2.325, 1), (0.35, 45.35, 1)))  # 10th channel
geometry.append(((24.149, 2.325, 1), (1.702, 0.35, 1)))  # 10th connection
geometry.append(((25.851, 2.325, 1), (0.35, 45.35, 1)))  # 11th channel
geometry.append(((26.201, 47.325, 1), (1.703, 0.35, 1)))  # 11th connection
geometry.append(((27.904, 2.325, 1), (0.35, 45.35, 1)))  # 12th channel
geometry.append(((28.254, 2.325, 1), (1.703, 0.35, 1)))  # 12th connection
geometry.append(((29.957, 2.325, 1), (0.35, 45.35, 1)))  # 13th channel
geometry.append(((30.307, 2.325, 1), (1.702, 0.35, 1)))  # 13th connection
geometry.append(((32.009, 2.325, 1), (0.35, 45.35, 1)))  # 14th channel
geometry.append(((32.359, 2.325, 1), (1.703, 0.35, 1)))  # 14th connection
geometry.append(((34.062, 2.325, 1), (0.35, 45.35, 1)))  # 15th channel
geometry.append(((34.412, 2.325, 1), (1.702, 0.35, 1)))  # 15th connection
geometry.append(((36.114, 2.325, 1), (0.35, 45.35, 1)))  # 16th channel
geometry.append(((36.464, 2.325, 1), (1.703, 0.35, 1)))  # 16th connection
geometry.append(((38.167, 2.325, 1), (0.35, 45.35, 1)))  # 17th channel
geometry.append(((38.517, 47.325, 1), (1.703, 0.35, 1)))  # 17th connection
geometry.append(((40.220, 9.825, 1), (0.35, 37.85, 1)))  # 18th channel
geometry.append(((40.570, 9.825, 1), (1.702, 0.35, 1)))  # 18th connection
geometry.append(((42.272, 9.825, 1), (0.35, 37.85, 1)))  # 19th channel
geometry.append(((42.622, 47.325, 1), (1.703, 0.35, 1)))  # 19th connection

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
with open('5x5_fang_20ch.ini', 'wb') as configfile:
    config.write(configfile)
