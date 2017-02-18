import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (Fang, 24 channels, 0.35 mm nozzle)')
config.set('Main', 'description', 'PDMS-based LSC-PM 5x5cm 24 channels Fang')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.05')
config.set('LSC', 'length', '0.05')
config.add_section('Channels')


geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z
geometry.append(((4.975, 0.000, 1), (1.05, 10.00, 1)))  # Inlet, bigger for the first 10 mm
geometry.append(((5.325, 10.00, 1), (0.35, 37.675, 1)))  # 1st channel top

geometry.append(((5.675, 47.325, 1), (1.346, 0.35, 1)))  # 1st connection
geometry.append(((7.021, 14.825, 1), (0.35, 32.85, 1)))  # 2nd channel (shorter!)
geometry.append(((7.371, 14.825, 1), (1.345, 0.35, 1)))  # 2nd connection
geometry.append(((8.716, 14.825, 1), (0.35, 32.85, 1)))  # 3rd channel
geometry.append(((9.066, 47.325, 1), (1.346, 0.35, 1)))  # 3rd connection
geometry.append(((10.412, 2.325, 1), (0.35, 45.35, 1)))  # 4th channel
geometry.append(((10.762, 2.325, 1), (1.346, 0.35, 1)))  # 4th connection

geometry.append(((12.108, 2.325, 1), (0.35, 45.35, 1)))  # 5th channel
geometry.append(((12.458, 47.325, 1), (1.345, 0.35, 1)))  # 5th connection

geometry.append(((13.803, 2.325, 1), (0.35, 45.35, 1)))  # 6th channel
geometry.append(((14.153, 2.325, 1), (1.346, 0.35, 1)))  # 6th connection

geometry.append(((15.499, 2.325, 1), (0.35, 45.35, 1)))  # 7th channel
geometry.append(((15.849, 47.325, 1), (1.346, 0.35, 1)))  # 7th connection

geometry.append(((17.195, 2.325, 1), (0.35, 45.35, 1)))  # 8th channel
geometry.append(((17.545, 2.325, 1), (1.345, 0.35, 1)))  # 8th connection

geometry.append(((18.890, 2.325, 1), (0.35, 45.35, 1)))  # 9th channel
geometry.append(((19.240, 47.325, 1), (1.346, 0.35, 1)))  # 9th connection

geometry.append(((20.586, 2.325, 1), (0.35, 45.35, 1)))  # 10th channel
geometry.append(((20.936, 2.325, 1), (1.346, 0.35, 1)))  # 10th connection

geometry.append(((22.282, 2.325, 1), (0.35, 45.35, 1)))  # 11th channel
geometry.append(((22.632, 47.325, 1), (1.345, 0.35, 1)))  # 11th connection

geometry.append(((23.977, 2.325, 1), (0.35, 45.35, 1)))  # 12th channel
geometry.append(((24.327, 2.325, 1), (1.346, 0.35, 1)))  # 12th connection

geometry.append(((25.673, 2.325, 1), (0.35, 45.35, 1)))  # 13th channel
geometry.append(((26.023, 47.325, 1), (1.345, 0.35, 1)))  # 13th connection

geometry.append(((27.368, 2.325, 1), (0.35, 45.35, 1)))  # 14th channel
geometry.append(((27.718, 2.325, 1), (1.346, 0.35, 1)))  # 14th connection

geometry.append(((29.064, 2.325, 1), (0.35, 45.35, 1)))  # 15th channel
geometry.append(((29.414, 47.325, 1), (1.346, 0.35, 1)))  # 15th connection

geometry.append(((30.760, 2.325, 1), (0.35, 45.35, 1)))  # 16th channel
geometry.append(((31.110, 2.325, 1), (1.345, 0.35, 1)))  # 16th connection

geometry.append(((32.455, 2.325, 1), (0.35, 45.35, 1)))  # 17th channel
geometry.append(((32.805, 47.325, 1), (1.346, 0.35, 1)))  # 17th connection

geometry.append(((34.151, 2.325, 1), (0.35, 45.35, 1)))  # 18th channel
geometry.append(((34.501, 2.325, 1), (1.346, 0.35, 1)))  # 18th connection

geometry.append(((35.847, 2.325, 1), (0.35, 45.35, 1)))  # 19th channel
geometry.append(((36.197, 47.325, 1), (1.345, 0.35, 1)))  # 19th connection

geometry.append(((37.542, 2.325, 1), (0.35, 45.35, 1)))  # 20th channel
geometry.append(((37.892, 2.325, 1), (1.346, 0.35, 1)))  # 20th connection

geometry.append(((39.238, 2.325, 1), (0.35, 45.35, 1)))  # 21th channel
geometry.append(((39.588, 47.325, 1), (1.346, 0.35, 1)))  # 21th connection

geometry.append(((40.934, 14.825, 1), (0.35, 32.85, 1)))  # 22th channel
geometry.append(((41.284, 14.825, 1), (1.345, 0.35, 1)))  # 22th connection

geometry.append(((42.629, 14.825, 1), (0.35, 32.85, 1)))  # 23th channel
geometry.append(((42.979, 47.325, 1), (1.346, 0.35, 1)))  # 23th connection

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
with open('5x5_fang_24ch.ini', 'wb') as configfile:
    config.write(configfile)
