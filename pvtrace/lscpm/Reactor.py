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
                 solvent=None, refractive_index_cgchong=1.340, exist_backscatter=False, exist_photovoltaic_bottom=False,
                 exist_photovoltaic_edge=False, blank=False):

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
        reaction_mixture = Material(absorption_data=abs_spectrum, emission_data=ems, quantum_efficiency=0.0,
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
                channel = Channel(origin=channel_data[0],
                                  size=channel_data[1], shape=channel_data[2])
                channel.material = reaction_mixture
                channel.name = channel_data[3]
                self.scene_obj.append(channel)
                self.reaction_volume += channel.volume

        try:
            capillaries_raw = config.get('Channels', 'capillaries')
        except ConfigParser.NoOptionError:
            capillaries_raw = ''

        if capillaries_raw is not '':
            capillaries = ast.literal_eval(capillaries_raw)

            for capillary_data in capillaries:
                capillary = Capillary(axis_origin=capillary_data[0], axis=capillary_data[1],
                                      length=capillary_data[2], outer_diameter=capillary_data[3],
                                      inner_diameter=capillary_data[4], tubing="PFA", reaction_material=reaction_mixture,
                                      refractive_index_cg=refractive_index_cgchong)
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
        if blank:
            self.lsc.material = CompositeMaterial([matrix.material()],
                                                  refractive_index=matrix.refractive_index())
        else:
            self.lsc.material = CompositeMaterial([matrix.material(), luminophore.material()],
                                                  refractive_index=matrix.refractive_index())
            # simulating the blank LSC

        self.lsc.name = lsc_name

        self.scene_obj.append(self.lsc)

        # 3.3 other accessories of LSC-PM
        if exist_backscatter:

            self.backscatter = PlanarReflector(reflectivity=1.0, origin=(0, 0, -0.0002), size=(lsc_x, lsc_y, 0.0001))
            self.backscatter.name = 'white paper'
            self.scene_obj.append(self.backscatter)

        if exist_photovoltaic_bottom:
            PV_box = Box(origin=(0, 0, 0), extent=(lsc_x, lsc_y, -0.0001))
            self.bottom_photovoltaic = SimpleCell(finiteplane=PV_box, origin=(0, 0, -0.001))
            self.bottom_photovoltaic.name = "bottom_cell"
            self.scene_obj.append(self.bottom_photovoltaic)

        if exist_photovoltaic_edge:
            PV_box_edge_near = Box(origin=(0, 0, 0), extent=(lsc_x, -0.001, thickness))
            self.edge_photovoltaic_near = SimpleCell(finiteplane=PV_box_edge_near, origin=(0, 0, 0))
            self.edge_photovoltaic_near.name = "edge_cell_near"
            self.scene_obj.append(self.edge_photovoltaic_near)

            PV_box_edge_far = Box(origin=(0, 0, 0), extent=(lsc_x, 0.001, thickness))
            self.edge_photovoltaic_far = SimpleCell(finiteplane=PV_box_edge_far, origin=(0, lsc_y, 0))
            self.edge_photovoltaic_far.name = "edge_cell_far"
            self.scene_obj.append(self.edge_photovoltaic_far)

            PV_box_edge_right = Box(origin=(0, 0, 0), extent=(0.001, lsc_y, thickness))
            self.edge_photovoltaic_right = SimpleCell(finiteplane=PV_box_edge_right, origin=(lsc_x, 0, 0))
            self.edge_photovoltaic_right.name = "edge_cell_right"
            self.scene_obj.append(self.edge_photovoltaic_right)

            PV_box_edge_left = Box(origin=(0, 0, 0), extent=(-0.001, lsc_y, thickness))
            self.edge_photovoltaic_left = SimpleCell(finiteplane=PV_box_edge_left, origin=(0, 0, 0))
            self.edge_photovoltaic_left.name = "edge_cell_left"
            self.scene_obj.append(self.edge_photovoltaic_left)


        self.log.info('Reactor volume (calculated): ' + str(self.reaction_volume * 1000000) + ' mL')

