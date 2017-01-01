from pvtrace import *


class LightSource(object):
    """
    Lightsources used by lscpm, are almost always implementation of PlanarSource
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
