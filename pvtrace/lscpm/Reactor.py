from __future__ import division, print_function

from pvtrace import *
import numpy as np
import os
import ConfigParser
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Photocatalysts import *
from pvtrace.lscpm.Solvents import *
import ast

# Print lamp data to export folder?
print_lamp = False


class LightSource(object):
    """
    Lightsources used by reactor
    """

    def __init__(self, lamp_type, irradiated_area=(0.05, 0.05), distance=0.025):
        self.logger = logging.getLogger('pvtrace.lightsource')
        if lamp_type == 'SolarSimulator':
            spectrum_file = os.path.join(PVTDATA, 'sources', 'Oriel_solar_sim.txt')
            lamp_name = 'Solar Simulator LS0110-100 L.O.T.-Oriel GmbH & Co.'
        elif lamp_type == 'Sun':
            spectrum_file = os.path.join(PVTDATA, 'sources', 'AM1.5g-full.txt')
            lamp_name = 'Solar Spectrum AM 1.5G'
        else:
            raise Exception('Unknown light source')

        self.spectrum = load_spectrum(spectrum_file, xbins=np.arange(350, 700))
        self.source = PlanarSource(direction=(0, 0, -1), spectrum=self.spectrum, length=irradiated_area[0],
                                   width=irradiated_area[1])
        self.source.name = lamp_name

        # Distance from device (it matters only for Visualizer as collimation of PlanarSource is perfect)
        self.source.translate((0, 0, distance))

    def plot(self):
        """
        Plots the lightsource spectrum
        """
        pvtrace.Analysis.xyplot(x=self.light.spectrum.x, y=self.light.spectrum.y,
                                filename='lightsource_' + self.name + '_spectrum')


class SolarSimulator(object):
    def __init__(self, size=(0.05, 0.05), wavelength_range=np.arange(350, 700), direction=(0, 0, -1)):
        """
        Create a SolarSimulator instance

        :param size: irradiated area
        :param wavelength_range: range of wavelength for emitted photons
        :param direction: direction of emitted photons
        """
        if len(parameters) < 2:
            raise Exception('Missing parameters for SolarSimulator! Dimensions (x,y in meters) are needed')

        spectrum_file = os.path.join(PVTDATA, 'sources', 'Oriel_solar_sim.txt')
        self.spectrum = load_spectrum(spectrum_file, xbins=wavelength_range)

        self.source = PlanarSource(direction=direction, spectrum=self.spectrum, length=size[0],
                                   width=size[1])
        self.source.name = 'Solar simulator LS0110-100 L.O.T.-Oriel GmbH & Co.'


class Sun(object):
    def __init__(self, parameters):
        """
        Create a SolarSimulator instance

        :param parameters: list with sizes (x and y)
        :return: PlanarSource
        """
        if len(parameters) < 2:
            raise Exception('Missing parameters for SolarSimulator! Dimensions (x,y in meters) are needed')
        spectrum_file = os.path.join(PVTDATA, 'sources', 'AM1.5g-full.txt')

        self.spectrum = load_spectrum(spectrum_file, xbins=np.arange(350, 700))
        self.source = PlanarSource(direction=(0, 0, -1), spectrum=self.spectrum, length=parameters[0],
                                   width=parameters[1])
        self.source.name = 'Solar Spectrum AM 1.5G'


class Reactor(object):
    """
    Object to model the experimental device
    """

    def __init__(self, reactor_name, luminophore, photocatalyst=None, photocatalyst_concentration=0.001, solvent=None):

        # 0. CONFIGURATION
        # 0.1 REACTOR TYPE
        config = ConfigParser.SafeConfigParser()
        # FIXME config read does not throw exceptions on file missing
        try:
            config.read(os.path.join(PVTDATA, 'reactors', reactor_name + '.ini'))
        except Exception:
            raise Exception('The configuration file for the requested reactor (', reactor_name, ') was not found.')

        # Set default values
        self.scene_obj = []
        self.reaction_volume = 0

        # 0. LOGGER
        reactor_logger = logging.getLogger('pvtrace.reactor')

        reactor_logger.info('Creating a reactor [' + str(reactor_name) + ']')
        reactor_logger.info('Luminophore = ' + str(luminophore.description()))

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
        channels_raw = config.get('Channels', 'channels')
        channels = ast.literal_eval(channels_raw)

        for channel_data in channels:
            channel = Channel(origin=channel_data[0],
                              size=channel_data[1], shape=channel_data[2])
            channel.material = reaction_mixture
            channel.name = channel_data[3]
            self.scene_obj.append(channel)
            self.reaction_volume += channel.volume

        # 3. LSC-PM

        # 3.1 LSC-PM GEOMETRY
        thickness = config.getfloat('LSC', 'thickness')
        lsc_x = config.getfloat('LSC', 'width')
        lsc_y = config.getfloat('LSC', 'length')
        lsc_name = config.get('Main', 'name')
        lsc_desc = config.get('Main', 'description')

        lsc = LSC(origin=(0, 0, 0), size=(lsc_x, lsc_y, thickness))

        # 3.2 MATRIX
        # Since matrix data is m-1 it gets corrected for thickness....

        # Fixme implement this! Only PDMS for now
        # matrix_material = MatrixMaterial(material)

        # Get Abs data for PDMS
        pdms_data = np.loadtxt(os.path.join(PVTDATA, 'PDMS.txt'))
        pdms_abs = Spectrum(x=pdms_data[:, 0], y=pdms_data[:, 1] * thickness)
        # Giving emission suppress error. Not used due to quantum_efficiency = 0 :)
        pdms_ems = Spectrum([0, 1000], [0.1, 0])
        matrix_refractive_index = 1.4118

        # Create LSC-PM Matrix material
        matrix_material = Material(absorption_data=pdms_abs, emission_data=pdms_ems, quantum_efficiency=0.0, refractive_index=1.41)


        # LSC CompositeMaterial made of dye+PDMS
        lsc.material = CompositeMaterial([matrix_material, luminophore.material()],
                                         refractive_index=matrix_refractive_index, silent=True)
        lsc.name = lsc_name
        self.scene_obj.append(lsc)

        reactor_logger.info('Reactor volume (calculated): ' + str(self.reaction_volume * 1000000) + ' mL')

        # 4. LAMP
        # FIXME add class parameters for lamp
        lamp_name = 'SolarSimulator'
        lamp_parameters = (0.05, 0.05)
        self.source = LightSource(lamp_type=lamp_name, irradiated_area=lamp_parameters)
        # self.source.plot() # Plots source spectrum to pvtrace_data folder
