from pvtrace import *
from pvtrace.Analysis import xyplot


class LightSource(object):
    """
    Lightsources used by LSC-PM, are almost always implementation of PlanarSource
    """

    def __init__(self, lamp_type):
        self.logger = logging.getLogger('pvtrace.lightsource')

        self.ready = False
        self.prefix = False
        self.spectrum = None
        self.source = None

        if lamp_type == 'SolarSimulator':
            self.spectrum_file = os.path.join(PVTDATA, 'sources', 'Oriel_solar_sim.txt')
            self.lamp_name = 'Solar Simulator LS0110-100 L.O.T.-Oriel GmbH & Co.'
        elif lamp_type == 'Sun':
            self.spectrum_file = os.path.join(PVTDATA, 'sources', 'AM1.5g-full.txt')
            self.lamp_name = 'Solar Spectrum AM 1.5G'
        elif lamp_type == 'Blue LEDs':
            self.prefix = 'Blue_LED_'
            self.lamp_name = 'Paulmann 702.11 blue LEDs'
        elif lamp_type == 'White LEDs':
            self.prefix = 'White_LED_'
            self.lamp_name = 'Paulmann 703.18 white LEDs'
        else:
            raise Exception('Unknown light source')

    def set_lightsource(self, irradiated_area=(0.05, 0.05), distance=0.025):
        if self.spectrum_file is None:
            raise ValueError('LightSource spectrum is not set!')
        self.spectrum = load_spectrum(self.spectrum_file, xbins=np.arange(350, 700))
        self.source = PlanarSource(direction=(0, 0, -1), spectrum=self.spectrum, length=irradiated_area[0],
                                   width=irradiated_area[1])
        self.source.name = self.lamp_name

        # Distance from device (it matters only for Visualizer as PlanarSource is collimated)
        self.source.translate((0, 0, distance))
        self.ready = True

    def move_lightsource(self, vector=(0, 0)):
        x = vector[0]
        y = vector[1]
        self.source.translate((x, y, 0))

    def set_LED_voltage(self, voltage=12):
        if self.ready is True:
            raise NameError('Cannot set voltage for this lightsource! Either already set or wrong lamp type!')

        voltage_string = str('%.1f' % voltage) + 'V'
        filename = self.prefix + voltage_string + '.txt'
        print(filename)
        self.spectrum_file = os.path.join(PVTDATA, 'sources', filename)
        self.lamp_name += '_' + voltage_string

    def plot(self):
        """
        Plots the lightsource spectrum (y-axis normalized)
        """
        normalization_factor = np.linalg.norm(self.source.spectrum.y, ord=1)
        y = self.source.spectrum.y/normalization_factor

        plt.switch_backend('Qt4Agg')
        xyplot(x=self.source.spectrum.x, y=y,
               filename='lightsource_' + self.source.name + '_spectrum')
