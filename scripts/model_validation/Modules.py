# pvtrace is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# pvtrace is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, print_function

from pvtrace import *
import numpy as np
import os


# Print lamp data to export folder?
print_lamp = False


class LightSource(object):
    """
    Lightsources
    """

    def __init__(self, lamp_name, parameters):
        self.name = lamp_name
        if lamp_name == 'SolarSimulator':
            self.light = SolarSimulator(parameters).source
        elif lamp_name == 'Sun':
            self.light = Sun(parameters).source
        elif lamp_name == 'LED_coiled':
            pass
        else:
            pass

    def plot(self):
        """
        Plots the lightsource spectrum
        """
        pvtrace.Analysis.xyplot(x=self.light.spectrum.x, y=self.light.spectrum.y,
                                filename='lightsource_' + self.name + '_spectrum')


class SolarSimulator(object):
    def __init__(self, parameters):
        """
        Create a SolarSimulator instance

        :param parameters: list with sizes (x and y)
        :return: PlanarSource
        """
        if len(parameters) < 2:
            raise Exception('Missing parameters for SolarSimulator! Dimensions (x,y in meters) are needed')
        # spectrum_file = os.path.join(PVTDATA, 'sources', 'AM1.5g-full.txt')
        spectrum_file = os.path.join(PVTDATA, 'sources', 'Oriel_solar_sim.txt')

        self.spectrum = load_spectrum(spectrum_file, xbins=np.arange(350, 700))

        self.source = PlanarSource(direction=(0, 0, -1), spectrum=self.spectrum, length=parameters[0],
                                   width=parameters[1])
        self.source.name = 'Solar simulator Michael (small)'
        # distance from device in this case is only important for Visualizer :)
        self.source.translate((0, 0, 0.025))


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
        self.source.name = 'Sun'
        # distance from device in this case is only important for Visualizer :)
        self.source.translate((0, 0, 0.025))


class Photocatalyst(object):
    def __init__(self, compound, concentration):
        if compound == 'MB':
            self.compound = MethyleneBlue()
        elif compound == 'Air':
            self.compound = Air()
        else:
            raise Exception('Unknown photocatalyst! (', compound, ')')
        self.concentration = concentration

    def spectrum(self):
        # Get spectrum in absorption coefficient (m-1) for 1M compound
        photocat_abs_data = self.compound.abs()
        # Then adjust it based on molar concentration
        photocat_abs_data[:, 1] = photocat_abs_data[:, 1] * self.concentration
        return Spectrum(x=photocat_abs_data[:, 0], y=photocat_abs_data[:, 1])

    def reactionMixture(self, solvent=None):
        if solvent is None:
            solvent = self.compound.solvent

        if solvent == 'acetonitrile':
            n = 1.344
        elif solvent == 'air':
            n = 1
        elif solvent == 'water':
            n = 1.33
        else:
            print("Unknown solvent. Water assumed as worst scenario (n=1.33)")
            n = 1.33

        # Reaction mixture as abortive medium with no emission
        ems = Spectrum([0, 1000], [0.1, 0])
        reaction_mixture = Material(absorption_data=self.spectrum(), emission_data=ems, quantum_efficiency=0.0,
                                    refractive_index=n)
        return reaction_mixture


class MethyleneBlue(object):
    def __init__(self):
        self.solvent = "acetonitrile"

    @staticmethod
    def abs():
        # Load 1M Abs spectrum of MB. Values from http://omlc.org/spectra/mb/mb-water.html
        # To convert this data to absorption coefficient in (cm-1), multiply by the molar concentration and 2.303.
        # abs_data= np.loadtxt(os.path.join(PVTDATA, "dyes", 'MB_abs.txt'))
        # abs_data[:, 1] = abs_data[:, 1] * 100 * mat.log(10)
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'MB_1M_1m_ACN.txt'))


class Air(object):
    """
    Air as photocatalyst: abs=0 for all wavelength.
    """

    def __init__(self):
        self.solvent = "air"

    @staticmethod
    def abs():
        # return Spectrum([0,1000], [0,0])
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'Air.txt'))


class DyeMaterial(object):
    """
    Abstract class for LSC's dye material
    """

    def __init__(self, dye_name, concentration, thickness):
        if dye_name == 'Red305':
            self.dye = Red305(concentration, thickness)
        else:
            raise Exception('Unknown dye! (', self.dye, ')')

    def material(self):
        # Note that refractive index is not important here since it will be overwritten with CompositeMaterial's one
        return Material(absorption_data=self.dye.absorption(), emission_data=self.dye.emission(),
                        quantum_efficiency=self.dye.quantum_efficiency, refractive_index=1.41)


class Red305(object):
    """
    Class to generate spectra for Red305-based devices
    """

    def __init__(self, concentration, thickness):
        self.quantum_efficiency = 0.95
        self.concentration = concentration
        self.thickness = thickness

    def absorption(self):
        if self.thickness is None or self.concentration is None:
            raise Exception('Missing data for dye absorption. Concentration and/or thickness unknown')
        # Red305 absorption spectrum (reference at 0.10 mg/g)
        absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'Red305_010mg_g_1m-1.txt'))

        # PREVIOUS IMPLEMENTATION!
        # Absorbance at peak (ap)
        # ap = absorption_data[:, 1].max()
        # Linearity measured up to 0.15mg/g, then it bends as bit due to too high Abs values for spectrometer
        # (secondary peak still linear at 0.20mg/g)
        # device_abs_at_peak = 13.031 * self.concentration * (self.thickness / 0.003)
        # print "with a concentration of ", self.concentration, ' and thickness', self.thickness, ' this device should have an Abs at peak of', device_abs_at_peak
        # Correcting factor to adjust absorption at peak to match settings
        # Note that in 'original' pvTrace, thin-film.py file np.log was used incorrectly (log10() intended, got ln())
        # phi = device_abs_at_peak / (ap * self.thickness)

        # Abs at 525 = 7.94956*dye loading
        # 1.0067 is the correction factor between exp. data at 0.10 mg/g and theoretical value
        phi = 1.006732182 * self.concentration/0.10

        print('phi equals ', phi, ' (this should approximately be simulation conc/tabulated conc (i.e. 0.10mg/g)')
        # Applying correction to spectrum
        absorption_data[:, 1] = absorption_data[:, 1] * phi

        # Create a reference spectrum for the computed absorption of device (z axis, thickness as optical path)
        # abs_scaled = absorption_data
        # abs_scaled[:, 1] = abs_scaled[:, 1] * self.thickness
        # xyplot(x=abs_scaled[:, 0], y=abs_scaled[:, 1], filename='spectrum_abs_lsc')
        # Create Spectrum elements
        return Spectrum(x=absorption_data[:, 0], y=absorption_data[:, 1])

    @staticmethod
    def emission():
        # fixme Add experimental data from pdms low concentration samples (not re-absorption red-shifted)
        # emission_data = np.loadtxt(os.path.join(PVTDATA, "dyes", 'fluro-red-fit.ems.txt'))
        emission_data = np.loadtxt(os.path.join(PVTDATA, "dyes", 'Red305_ems_spectrum.txt'))
        return Spectrum(x=emission_data[:, 0], y=emission_data[:, 1])


class Reactor(object):
    """
    Class that models the experimental device
    """

    # noinspection PyPep8,PyPep8,PyPep8
    def __init__(self, reactor_name, dye, dye_concentration, photocatalyst=None, photocatalyst_concentration=0.001,
                 solvent=None):

        # Set photocatalyst
        if photocatalyst is None:
            self.photocat = False
        else:
            self.photocat = Photocatalyst(photocatalyst, photocatalyst_concentration)

        # Solvent is default for photocatalyst or explicitly set
        if solvent is None:
            reaction_mixture = self.photocat.reactionMixture()
        else:
            reaction_mixture = self.photocat.reactionMixture(solvent)

        # Set default values
        self.scene_obj = []
        self.reaction_volume = 0

        # Get Abs data for PDMS (depending on reactor thickness they will be adjusted and the material will be created
        # out of the reactor loop
        pdms_data = np.loadtxt(os.path.join(PVTDATA, 'PDMS.txt'))

        if reactor_name == '5x5_8ch':
            # 1. LSC DEVICE
            # @formatter:off
            thickness = 0.003   # 3 mm thickness
            lsc_x = 0.05        # 5 cm width
            lsc_y = 0.05        # 5 cm length
            lsc_name = 'Reactor (5x5cm, 8 channels, Dye: ' + dye + ')'
            # @formatter:on

            # 2. CHANNELS
            for i in range(1, 9):
                channel = Channel(origin=(0.005, 0.007 + 0.005 * (i - 1), 0.001),
                                  size=(0.040, 0.001, 0.001), shape="box")
                channel.material = reaction_mixture
                channel.name = "Channel" + str(i)
                self.scene_obj.append(channel)
                self.reaction_volume += channel.volume

            # 3. LIGHT (Perpendicular planar source 5x5 (matching device) with sun spectrum)
            lamp_name = 'SolarSimulator'
            # Size of the irradiated area
            lamp_parameters = (0.05, 0.05)
        elif reactor_name == '5x5_6ch_squared':
            # 1. LSC DEVICE
            # @formatter:off
            thickness = 0.003   # 3 mm thickness
            lsc_x = 0.05        # 5 cm width
            lsc_y = 0.05        # 5 cm length
            lsc_name = 'Reactor (5x5cm, 6 squared channels, Dye: ' + dye + ')'
            # @formatter:on

            # 2. CHANNELS
            # Geometry of channels: origin and sizes in mm
            geometry = []
            # @formatter:off
            #        ORIGIN:  X      Y    Z  L:   X     Y   Z
            geometry.append(((   0,  5.00, 1), (10.0, 1.0, 1)))  # Inlet, bigger for the first 10 mm
            geometry.append(((10.0,  5.25, 1), (37.5, 0.5, 1)))  # 1st channel
            geometry.append(((47.0,  5.75, 1), ( 0.5, 7.3, 1)))  # 1st Vertical connection
            geometry.append((( 2.5, 13.05, 1), (45.0, 0.5, 1)))  # 2nd channel
            geometry.append((( 2.5, 13.55, 1), ( 0.5, 7.3, 1)))  # 2nd Vertical connection
            geometry.append((( 2.5, 20.85, 1), (45.0, 0.5, 1)))  # 3rd channel
            geometry.append(((47.0, 21.35, 1), ( 0.5, 7.3, 1)))  # 3rd Vertical connection
            geometry.append((( 2.5, 28.65, 1), (45.0, 0.5, 1)))  # 4th channel
            geometry.append((( 2.5, 29.15, 1), ( 0.5, 7.3, 1)))  # 4th Vertical connection
            geometry.append((( 2.5, 36.45, 1), (45.0, 0.5, 1)))  # 5th channel
            geometry.append(((47.0, 36.95, 1), ( 0.5, 7.3, 1)))  # 5th Vertical connection
            geometry.append(((10.0, 44.25, 1), (37.5, 0.5, 1)))  # 6th channel
            geometry.append(((   0, 44.00, 1), (10.0, 1.0, 1)))  # Outlet, bigger for the first 10 mm
            # @formatter:on

            # Transform mm into meters (overly complicated code to multiply all values im geometry per 0.001)
            geometry = [[[coord * 0.001 for coord in tuples] for tuples in channel] for channel in geometry]

            for i in range(0, len(geometry)):
                position = geometry[i]
                channel = Channel(origin=position[0], size=position[1], shape="box")
                channel.material = reaction_mixture
                channel.name = "Channel" + str(i)
                self.scene_obj.append(channel)
                self.reaction_volume += channel.volume

            # 3. LIGHT (Perpendicular planar source 5x5 (matching device) with sun spectrum)
            lamp_name = 'SolarSimulator'
            # Size of the irradiated area
            lamp_parameters = (0.05, 0.05)
        elif reactor_name == '5x5_slab':
            # 1. LSC DEVICE
            # @formatter:off
            thickness = 0.003   # 3 mm thickness
            lsc_x = 0.05        # 5 cm width
            lsc_y = 0.05        # 5 cm length
            lsc_name = 'Reactor (5x5cm, 0 channel, Dye: ' + dye + ')'
            # @formatter:on
            self.reaction_volume = 0

            # 3. LIGHT (Perpendicular planar source 5x5 (matching device) with sun spectrum)
            lamp_name = 'SolarSimulator'
            # Size of the irradiated area
            lamp_parameters = (0.05, 0.05)
        else:
            raise Exception('The reactor requested (', reactor_name, ') is not known. Check the name ;)')

        # 1. PDMS
        # Since PDMS data is m-1 it gets corrected for thickness....
        pdms_abs = Spectrum(x=pdms_data[:, 0], y=pdms_data[:, 1] * thickness)
        # Giving emission suppress error. Not used due to quantum_efficiency = 0 :)
        pdms_ems = Spectrum([0, 1000], [0.1, 0])
        # Create Material
        pdms = Material(absorption_data=pdms_abs, emission_data=pdms_ems, quantum_efficiency=0.0, refractive_index=1.41)

        # 2. LSC
        lsc = LSC(origin=(0, 0, 0), size=(lsc_x, lsc_y, thickness))
        # Material for dye
        dye_material = DyeMaterial(dye, dye_concentration, thickness)
        # LSC CompositeMaterial made of dye+PDMS
        lsc.material = CompositeMaterial([pdms, dye_material.material()], refractive_index=1.41, silent=True)
        lsc.name = lsc_name
        self.scene_obj.append(lsc)

        # 3. LAMP
        lamp = LightSource(lamp_name, lamp_parameters)
        self.source = lamp.light
        if print_lamp:
            lamp.plot()
