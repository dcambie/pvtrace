import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (Fang bifurcation, 8 channels, 1.5mm spacing)')
config.set('Main', 'description', 'PDMS-based LSC-PM for scale-up, 8 channels 1.5mm spacing - Fang')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.0163')
config.set('LSC', 'length', '0.18505')
config.add_section('Channels')


geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z

geometry.append(((7.625, 0.000, 1), (1.05, 7.00, 1)))  # Inlet

geometry.append(((3.650, 7.000, 1), (9.00, 1.60, 1)))  # 1st bifurcation

geometry.append(((3.650, 8.600, 1), (1.60, 4.50, 1)))  # Left branch
geometry.append(((11.05, 8.600, 1), (1.60, 4.50, 1)))  # Right branch

geometry.append(((2.200, 13.10, 1), (4.5, 0.80, 1)))  # 2nd bifurcation, left
geometry.append(((9.600, 13.10, 1), (4.5, 0.80, 1)))  # 2nd bifurcation, right

geometry.append(((2.200, 13.90, 1), (0.8, 3.10, 1)))  # Left, left branch
geometry.append(((5.900, 13.90, 1), (0.8, 3.10, 1)))  # Left, right branch
geometry.append(((9.600, 13.90, 1), (0.8, 3.10, 1)))  # Right, left branch
geometry.append(((13.300, 13.90, 1), (0.8, 3.10, 1)))  # Right, right branch

geometry.append(((1.500, 17.00, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, left left
geometry.append(((5.200, 17.00, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, left right
geometry.append(((8.900, 17.00, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, right left
geometry.append(((12.60, 17.00, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, right right

geometry.append(((1.500, 17.35, 1), (0.35, 150.35, 1)))  # 1st channel
geometry.append(((3.350, 17.35, 1), (0.35, 150.35, 1)))  # 2nd channel
geometry.append(((5.200, 17.35, 1), (0.35, 150.35, 1)))  # 3rd channel
geometry.append(((7.050, 17.35, 1), (0.35, 150.35, 1)))  # 4th channel
geometry.append(((8.900, 17.35, 1), (0.35, 150.35, 1)))  # 5th channel
geometry.append(((10.75, 17.35, 1), (0.35, 150.35, 1)))  # 6th channel
geometry.append(((12.60, 17.35, 1), (0.35, 150.35, 1)))  # 7th channel
geometry.append(((14.45, 17.35, 1), (0.35, 150.35, 1)))  # 8th channel

geometry.append(((7.625, 178.05, 1), (1.05, 7.00, 1)))  # Outlet

geometry.append(((3.650, 176.45, 1), (9.00, 1.60, 1)))  # 1st bifurcation

geometry.append(((3.650, 171.95, 1), (1.60, 4.50, 1)))  # Left branch
geometry.append(((11.05, 171.95, 1), (1.60, 4.50, 1)))  # Right branch

geometry.append(((2.200, 171.15, 1), (4.5, 0.80, 1)))  # 2nd bifurcation, left
geometry.append(((9.600, 171.15, 1), (4.5, 0.80, 1)))  # 2nd bifurcation, right

geometry.append(((2.200, 168.05, 1), (0.8, 3.10, 1)))  # Left, left branch
geometry.append(((5.900, 168.05, 1), (0.8, 3.10, 1)))  # Left, right branch
geometry.append(((9.600, 168.05, 1), (0.8, 3.10, 1)))  # Right, left branch
geometry.append(((13.30, 168.05, 1), (0.8, 3.10, 1)))  # Right, right branch

geometry.append(((1.500, 167.7, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, left left
geometry.append(((5.200, 167.7, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, left right
geometry.append(((8.900, 167.7, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, right left
geometry.append(((12.60, 167.7, 1), (2.2, 0.35, 1)))  # 3rd bifurcation, right right



# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

channel = []
for i in range(0, len(geometry)):
    position = geometry[i]
    channel.append((position[0], position[1], 'box', 'Channel' + str(i)))

config.set('Channels', 'channels', str(channel))

# Writing our configuration file to 'example.cfg'
with open('Fang_8ch_1.5mm.ini', 'wb') as configfile:
    config.write(configfile)
