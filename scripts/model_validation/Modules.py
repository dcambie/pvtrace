from __future__ import division
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
from pvtrace import *
import numpy as np


class LightSource(object):
    """
    Lightsources
    """

    def __init__(self, name):
        if name == 'SolarSimulator':
            pass
        elif name == 'LED_coiled':
            pass
        else:
            return


class Photocatalyst(object):
    def __init__(self, compound, concentration):
        if compound == 'MB':
            self.compound = MethyleneBlue()
        else:
            raise Exception('Unknown photocatalyst! (', compound, ')')
        self.concentration = concentration

    def spectrum(self):
        # Get spectrum in absorption coefficient (m-1) for 1M compound
        photocat_abs_data = self.compound.abs()
        # Then adjust it based on molar concentration
        photocat_abs_data[:, 1] = photocat_abs_data[:, 1] * self.concentration
        return Spectrum(x=photocat_abs_data[:, 0], y=photocat_abs_data[:, 1])


class MethyleneBlue(object):
    def __init__(self):
        pass

    @staticmethod
    def abs():
        # Load 1M Abs spectrum of MB. Values from http://omlc.org/spectra/mb/mb-water.html
        # To convert this data to absorption coefficient in (cm-1), multiply by the molar concentration and 2.303.
        # abs_data= np.loadtxt(os.path.join(PVTDATA, "dyes", 'MB_abs.txt'))
        # abs_data[:, 1] = abs_data[:, 1] * 100 * mat.log(10)
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'MB_1M_1m_ACN.txt'))


class DyeMaterial(object):
    """
    Abstract class for LSC's dye material
    """

    def __init__(self, dye_name):
        if dye_name == 'Red305':
            self.dye = Red305()
        else:
            raise Exception('Unknown dye! (', dye, ')')

    def material(self):
        # Note that refractive index is not important here since it will be overwritten with CompositeMaterial's one
        return Material(absorption_data=self.dye.absorption(), emission_data=self.dye.emission(),
                        quantum_efficiency=self.dye.quantum_efficiency, refractive_index=1.41)


class Red305(object):
    """
    Class to generate spectra for Red305-based devices
    """

    def __init__(self):
        self.quantum_efficiency = 0.95

    def absorption(self):
        if self.thickness is None or self.concentration is None:
            raise Exception('Missing data for dye absorption. Concentration and/or thickness unknown')
        # Red305 absorption spectrum (reference at 0.10 mg/g)
        absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'Red305_010mg_g_1m-1.txt'))
        # Absorbance at peak (ap)
        ap = absorption_data[:, 1].max()
        # Linearity measured up to 0.15mg/g, then it bends as bit due to too high Abs values for spectrometer
        # (secondary peak still linear at 0.20mg/g)
        device_abs_at_peak = 13.031 * self.concentration
        print "with a concentration of ", self.concentration, ' and thickness', self.thickness, ' this device should have an Abs at peak of', device_abs_at_peak
        # Correcting factor to adjust absorption at peak to match settings
        # Note that in 'original' pvTrace, thin-film.py file np.log was used incorrectly (log10() intended, got ln())
        phi = device_abs_at_peak / (ap * self.thickness)
        # print 'phi equals ',phi,' (this should approximately be simulation conc/tabulated conc (i.e. 0.10mg/g)'
        # Applying correction to spectrum
        absorption_data[:, 1] = absorption_data[:, 1] * phi
        # Create Spectrum elements
        return Spectrum(x=absorption_data[:, 0], y=absorption_data[:, 1])

    @staticmethod
    def emission():
        # fixme Add experimental data from pdms low concentration samples (not reabsorption redshifted)
        emission_data = np.loadtxt(os.path.join(PVTDATA, "dyes", 'fluro-red-fit.ems.txt'))
        return Spectrum(x=emission_data[:, 0], y=emission_data[:, 1])


class Reactor(object):
    """
    Class that models the experimental device
    """

    def __init__(self, name, dye, dye_concentration, photocatalyst=None, photocatalyst_concentration=0.001):
        if photocatalyst is None:
            self.photocat = False
        else:
            self.photocat = Photocatalyst(photocatalyst, photocatalyst_concentration)
        self.scene_obj = []

        # Create a Material for pdms
        abs = Spectrum([0, 1000], [2, 2])
        # Giving emission suppress error. Not used due to quantum_efficiency = 0 :)
        ems = Spectrum([0, 1000], [0.1, 0])
        pdms = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.41)

        if name == '5x5_8ch':
            # 1. LSC DEVICE
            thickness = 0.003
            lsc = LSC(origin=(0, 0, 0), size=(0.050, 0.050, thickness))
            # Clear reactor (control) is obtained with dye concentration = 0
            dye_material = DyeMaterial(dye)
            dye_material.dye.concentration = dye_concentration
            dye_material.dye.thickness = thickness

            lsc.material = CompositeMaterial([pdms, dye_material.material()], refractive_index=1.41, silent=True)
            lsc.name = 'Reactor (5x5cm, 8 channel, Dye: ' + dye + ')'
            self.scene_obj.append(lsc)

            # 2. CHANNELS
            reaction_mixture = self.getreactionmixture(solvent='acetonitrile')
            for i in range(1, 9):
                channel = Channel(origin=(0.005, 0.007 + 0.005 * (i - 1), 0.001), size=(0.040, 0.001, 0.001),
                                  shape="box")
                channel.material = reaction_mixture
                channel.name = "Channel" + str(i)
                self.scene_obj.append(channel)

            # 3. LIGHT (Perpendicular planar source 5x5 (matching device) with sun spectrum)
            file = os.path.join(PVTDATA, 'sources', 'AM1.5g-full.txt')
            sun = load_spectrum(file, xbins=np.arange(400, 800))
            self.source = PlanarSource(direction=(0, 0, -1), spectrum=sun, length=0.050, width=0.050)
            self.source.name = 'Solar simulator Michael (small)'
            # distance from device in this case is only important for Visualizer :)
            self.source.translate((0, 0, 0.025))
        elif name == "5x5_0ch":
            # 1. LSC DEVICE
            thickness = 0.003
            lsc = LSC(origin=(0, 0, 0), size=(0.050, 0.050, thickness))
            # Clear reactor (control) is obtained with dye concentration = 0
            dye_material = DyeMaterial(dye)
            dye_material.dye.concentration = dye_concentration
            dye_material.dye.thickness = thickness

            # PDMS background absorption
            abs = Spectrum([0, 1000], [2, 2])
            ems = Spectrum([0, 1000],
                           [0.1, 0])  # Giving emission suppress error. It's not used due to quantum_efficiency=0 :)
            pdms = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.41)

            lsc.material = CompositeMaterial([pdms, dye_material.material()], refractive_index=1.41, silent=True)
            lsc.name = 'Reactor (5x5cm, 8 channel, Dye: ' + dye + ')'
            self.scene_obj.append(lsc)

            # 2. LIGHT (Perpendicular planar source 5x5 (matching device) with sun spectrum)
            file = os.path.join(PVTDATA, 'sources', 'AM1.5g-full.txt')
            sun = load_spectrum(file, xbins=np.arange(400, 800))
            self.source = PlanarSource(direction=(0, 0, -1), spectrum=sun, length=0.050, width=0.050)
            self.source.name = 'Solar simulator Michael (small)'
            # distance from device in this case is only important for Visualizer :)
            self.source.translate((0, 0, 0.025))
        else:
            raise Exception('The reactor requested (', name, ') is not known. Check the name ;)')

    def getreactionmixture(self, solvent=None):
        if solvent is None:
            n = 1.33
        elif solvent == 'acetonitrile':
            n = 1.344
        elif solvent == 'water':
            n = 1.33
        else:
            print "Unknown solvent. Water assumed as worst scenario (n=1.33)"
            n = 1.33

        if not self.photocat:
            raise Exception('No Photocatalyst data for reaction mixture')

        # Reaction mixture as abortive medium with no emission
        ems = Spectrum([0, 1000], [0.1, 0])
        reaction_mixture = Material(absorption_data=self.photocat.spectrum(), emission_data=ems, quantum_efficiency=0.0,
                                    refractive_index=n)
        return reaction_mixture


class Statistics(object):
    """
    Class for analysis of results, based on the produced database.
    Can also be applied to old database data
    """

    def __init__(self, database):
        self.db = database
        self.photon_generated = len(self.db.uids_generated_photons())
        self.photon_killed = len(self.db.killed())
        self.tot = self.photon_generated - self.photon_killed
        self.non_radiative = len(self.db.uids_nonradiative_losses())

    def percent(self, num_photons):
        """
        Return the percentage of num_photons with respect to thrown photons as 2 decimal digit string
        :param num_photons:
        :rtype: string
        """

        return format((num_photons / self.tot) * 100, '.2f')

    def print_report(self):
        print "##### PVTRACE LOG RESULTS #####"

        print "Summary:"
        print 'obj ', self.db.objects_with_records()
        print 'surfaces ', self.db.surfaces_with_records()

        obj_w_records = self.db.objects_with_records()
        for obj in obj_w_records:
            print 'OBJ ', obj, ' was hit on: ', self.db.surfaces_with_records_for_object(obj)

            # print "\t Photon efficiency \t", (luminescent_edges + luminescent_apertures) * 100 / thrown, "%"
            # print "\t Optical efficiency \t", luminescent_edges * 100 / thrown, "%"

    def print_detailed(self):
        self.print_report()

        print "Technical details:"
        print "\t Generated \t", self.photon_generated
        print "\t Killed \t", self.photon_killed
        print "\t Thrown \t", self.tot

        print "Luminescent photons:"

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']

        for surface in edges:
            print "\t", surface, "\t", self.percent(len(
                self.db.uids_out_bound_on_surface(surface, luminescent=True))), "%"

        for surface in apertures:
            print "\t", surface, "\t", self.percent(len(
                self.db.uids_out_bound_on_surface(surface, luminescent=True))), "%"

        # print "Non radiative losses\t", self.percent(non_radiative_photons), "%"

        print "Solar photons (transmitted/reflected):"
        for surface in edges:
            print "\t", surface, "\t", self.percent(len(
                self.db.uids_out_bound_on_surface(surface, solar=True))), "%"

        for surface in apertures:
            print "\t", surface, "\t", self.percent(len(
                self.db.uids_out_bound_on_surface(surface, solar=True))), "%"

        print "Reactor's channel photons:"

        photons = self.db.uids_in_reactor()
        photons_in_channels_tot = len(photons)
        luminescent_photons_in_channels = len(self.db.uids_in_reactor_and_luminescent())
        # oNLY PHOTONS IN CHANNELS!
        for photon in photons:
            print "Wavelenght: ", self.db.wavelengthForUid(photon)  # Nice output
            # print " ".join(map(str, self.db.wavelengthForUid(photon)))  # Clean output (for elaborations)

        print "Photons in channels (sum)", self.percent(photons_in_channels_tot), "% (", photons_in_channels_tot, ")"
        print 'Luminescent',luminescent_photons_in_channels

        top_reflected = len(self.db.uids_out_bound_on_surface("top", solar=True))
        bottom_lost = len(self.db.uids_out_bound_on_surface("bottom", solar=True))

        # print thrown, "\t", top_reflected, "\t", bottom_lost, "\t", luminescent_edges, "\t", luminescent_apertures, "\t", (
        # photons_in_channels_tot - luminescent_photons_in_channels), "\t", luminescent_photons_in_channels, "\t", non_radiative_photons

        # if top_reflected + bottom_lost + luminescent_edges + luminescent_apertures + photons_in_channels_tot + non_radiative_photons == thrown:
        #     print "Results validity check OK :)"
        # else:
        #     print "!!! ERROR !!! Check results carefully!"

    def create_graphs(self):
        import os
        import numpy as np
        import pylab

        home = os.path.expanduser("~")

        print "Plotting reactor..."
        uid = self.db.uids_in_reactor()
        # print "Photons in channels array is: ",uid
        data = self.db.wavelengthForUid(uid)
        hist = np.histogram(data, bins=np.linspace(300, 800, num=100))
        pylab.hist(data, 100, histtype='stepfilled')
        location = os.path.join(home, "pvtrace_export", "plot-reactor.png")
        pylab.savefig(location)
        print 'Plot saved in ', location, '!'
        pylab.clf()

        print "Plotting reactor luminescent..."
        uid = db.uids_in_reactor_and_luminescent()
        # print "Photons in channels array is: ",uid
        data = db.wavelengthForUid(uid)
        hist = np.histogram(data, bins=np.linspace(300, 800, num=100))
        pylab.hist(data, 100, histtype='stepfilled')
        location = os.path.join(home, "pvtrace_export", "plot-reactor-luminescent.png")
        pylab.savefig(location)
        print 'Plot saved in ', location, '!'
        pylab.clf()
