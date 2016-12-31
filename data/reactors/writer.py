import os, ConfigParser

config = ConfigParser.SafeConfigParser()
config.add_section('Main')
config.set('Main', 'name', 'Reactor (5x5cm, Spyral, 0.35 mm nozzle)')
config.set('Main', 'description', 'PDMS-based LSC-PM 5x5cm w/ spyral design')
config.add_section('LSC')
config.set('LSC', 'thickness', '0.003')
config.set('LSC', 'width', '0.05')
config.set('LSC', 'length', '0.05')
config.add_section('Channels')


geometry = []
#        ORIGIN:  X        Y     Z  L:   X      Y   Z
geometry.append(((4.775, 0.000, 1), (1.05, 10.00, 1)))  # Inlet, bigger for the first 10 mm
geometry.append(((5.125, 10.000, 1), (0.35, 36.15, 1)))  # 1st channel left
geometry.append(((5.475, 45.800, 1), (31.25, 0.35, 1)))  # 1st channel bottom
geometry.append(((36.725, 11.650, 1), (0.35, 34.50, 1)))  # 2nd channel right
geometry.append(((21.075, 11.650, 1), (15.65, 0.35, 1)))  # 2nd channel top
geometry.append(((20.725, 11.650, 1), (0.35, 18.90, 1)))  # 3rd channel left
geometry.append(((21.075, 30.200, 1), (3.75, 0.35, 1)))  # 3nd channel bottom
geometry.append(((24.825, 19.450, 1), (0.35, 11.10, 1)))  # Middle piece
geometry.append(((25.175, 19.450, 1), (3.75, 0.35, 1)))  # 3nd channel top
geometry.append(((28.925, 19.450, 1), (0.35, 18.90, 1)))  # 3nd channel right
geometry.append(((13.275, 38.000, 1), (15.65, 0.35, 1)))  # 2nd channel bottom
geometry.append(((12.925, 3.850, 1), (0.35, 34.50, 1)))  # 2nd channel left
geometry.append(((13.275, 3.850, 1), (31.25, 0.35, 1)))  # 1st channel top
geometry.append(((44.525, 3.850, 1), (0.35, 36.15, 1)))  # 1st channel right
geometry.append(((44.175, 40.000, 1), (1.05, 10.00, 1)))  # Outlet, bigger for the first 10 mm

# Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

channel = []
for i in range(0, len(geometry)):
    position = geometry[i]
    channel.append((position[0], position[1], 'box', 'Channel' + str(i)))

config.set('Channels', 'channels', str(channel))

# Writing our configuration file to 'example.cfg'
with open('5x5_spyral_035_3_1.ini', 'wb') as configfile:
    config.write(configfile)
