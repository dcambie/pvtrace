from __future__ import division, print_function

from pvtrace import *
import numpy as np
import os
import ConfigParser
from pvtrace.lscpm.Photocatalysts import *
from pvtrace.lscpm.Solvents import *
from pvtrace.lscpm.Capillary import *
import ast


class Reactor(object):
    """
    Object to model the experimental device
    """

    def __init__(self, reactor_name, luminophore, matrix, photocatalyst, photocatalyst_concentration=0.001,
                 solvent=None):

        # 0. CONFIGURATION
        # 0.1 REACTOR TYPE
        config = ConfigParser.SafeConfigParser()
        # FIXME config read does not throw exceptions on file missing
        try:
            config.read(os.path.join(PVTDATA, 'reactors', reactor_name + '.ini'))
        except Exception:
            raise Exception('The configuration file for the requested reactor (', reactor_name, ') was not found.')

        # 0.2 default values
        self.scene_obj = []
        self.reaction_volume = 0

        # 0.3 LOGGER
        self.log = logging.getLogger('pvtrace.reactor')
        self.log.info('Creating a reactor [' + str(reactor_name) + ']')
        self.log.info('Luminophore = ' + str(luminophore.description()))

        # 1. REACTION MIXTURE
        # 1.1 Photocatalyst
        self.photocat = Photocatalyst(compound=photocatalyst, concentration=photocatalyst_concentration)
        abs_spectrum = self.photocat.spectrum()

        # 1.2 Solvent
        self.reaction_solvent = Solvent(solvent_name=solvent)
        n = self.reaction_solvent.refractive_index()

        # Reaction mixture as abortive medium with no emission. All abs due to photocatalyst
        ems = Spectrum([0, 1000], [0.1, 0])
        self.reaction_mixture = Material(absorption_data=abs_spectrum, emission_data=ems, quantum_efficiency=0.0,
                                    refractive_index=n)

        # 2. CHANNELS
        # Create the channels described in reactor_type with the given reaction_mixture and adds them to the scene
        try:
            channels_raw = config.get('Channels', 'channels')
        except ConfigParser.NoOptionError:
            channels_raw = ''

        if channels_raw is not '':
            channels = ast.literal_eval(channels_raw)

            for channel_data in channels:
                if channel_data[2] != "circle_cylinder":
                    channel = Channel(origin=channel_data[0],
                                      size=channel_data[1], shape=channel_data[2])
                    channel.material = self.reaction_mixture
                    channel.name = channel_data[3]
                    self.scene_obj.append(channel)
                    self.reaction_volume += channel.volume

                else:
                    self.curving_channel(channel_data, start_angle=0, end_angle=np.pi)

        try:
            capillaries_raw = config.get('Channels', 'capillaries')
        except ConfigParser.NoOptionError:
            capillaries_raw = ''

        if capillaries_raw is not '':
            capillaries = ast.literal_eval(capillaries_raw)

            for capillary_data in capillaries:
                capillary = Capillary(axis_origin=capillary_data[0], axis=capillary_data[1],
                                      length=capillary_data[2], outer_diameter=capillary_data[3],
                                      inner_diameter=capillary_data[4], reaction_material=self.reaction_mixture)
                capillary.tubing.name = capillary_data[5]+'_tubing'
                capillary.reaction.name = capillary_data[5] + '_reaction'
                self.scene_obj.append(capillary.tubing)
                self.scene_obj.append(capillary.reaction)
                self.reaction_volume += capillary.reaction.volume

        # 3. LSC-PM
        # 3.1 LSC-PM GEOMETRY
        thickness = config.getfloat('LSC', 'thickness')
        lsc_x = config.getfloat('LSC', 'width')
        lsc_y = config.getfloat('LSC', 'length')
        lsc_name = config.get('Main', 'name')
        lsc_desc = config.get('Main', 'description')

        # 3.2 LSC object creation
        self.lsc = LSC(origin=(0, 0, 0), size=(lsc_x, lsc_y, thickness))
        # CompositeMaterial made of matrix + luminophore
        self.lsc.material = CompositeMaterial([matrix.material(), luminophore.material()],
                                              refractive_index=matrix.refractive_index())
        self.lsc.name = lsc_name
        self.scene_obj.append(self.lsc)

        # collision bug about width and length (lsc and SolarSimulator)
        self.lsc_length = lsc_x
        self.lsc_width = lsc_y

        self.log.info('Reactor volume (calculated): ' + str(self.reaction_volume * 1000000) + ' mL')

    def curving_channel(self, channel_data, start_angle=0, end_angle=2*np.pi):
        size = channel_data[1]
        origin_change = list(channel_data[0])

        length = size[0]
        circle_radius = size[1]
        cylinder_radius = size[2]

        theta = np.arange(start_angle, end_angle, np.pi/200)
        for theta0 in theta:
            origin_change[0] = channel_data[0][0] + circle_radius - np.cos(theta0) * circle_radius
            origin_change[1] = channel_data[0][1] + np.sin(theta0) * circle_radius
            channel = Channel(origin=tuple(origin_change),
                              size=(length, cylinder_radius, cylinder_radius), shape="cylinder")
            channel.material = self.reaction_mixture
            self.reaction_volume += channel.volume
            channel.name = "circle_cylinder" + str(theta0/(np.pi/200))
            self.scene_obj.append(channel)