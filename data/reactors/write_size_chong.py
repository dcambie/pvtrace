import os, ConfigParser, sys
import numpy as np

for mainloop_i in range(1, 6):
    # mainloop_i = mainloop_i*5 + 5
    width_LSC = float(mainloop_i)/100
    origin_x_cap = mainloop_i*10/2
    config = ConfigParser.SafeConfigParser()
    config.add_section('Main')
    config.set('Main', 'name', str(mainloop_i)+'x39x0.8_red_single_capillary')
    config.set('Main', 'description', 'investigate the influence of intercapillary spacing')
    config.add_section('LSC')
    config.set('LSC', 'thickness', '0.008')
    config.set('LSC', 'width', str(width_LSC))
    config.set('LSC', 'length', '0.39')

    config.add_section('Channels')

    # Simplified with axis and length in common among all the capillaries
    chong_epi = 10**-6
    default_od = 0.00317
    default_id = 0.00159
    axis = 1
    length = 0.39 - 2*chong_epi

    geometry = []
    #        ORIGIN:  X        Y     Z  AXIS LENGTH
    geometry.append((origin_x_cap, chong_epi*1000, 4))  # Inlet


    # Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
    geometry = [[coord * 0.001 for coord in capillary] for capillary in geometry]

    capillary = []
    for i in range(0, len(geometry)):
        position = geometry[i]

        # Origin, axis, length, OD, ID, name
        capillary.append(((position[0], position[1], position[2]), axis, length, default_od, default_id, 'Capillary' + str(i)))

    config.set('Channels', 'capillaries', str(capillary))
    with open('interspace_'+str(mainloop_i)+'x39x0.8_chong.ini', 'wb') as configfile:
        config.write(configfile)
        configfile.close()
sys.exit(0)