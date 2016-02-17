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
    """ Lightsources of lab to match exp. results """

    def __init__(self, name):
        if name == 'SolarSimulator':
            pass
        elif name == 'LED_coiled':
            pass
        else:
            return

class Reactor(object):
    """ Class that models experimental devices """

    def __init__(self, name, dye, dye_concentration, photocatalyst=None):
        if photocatalyst == None:
            photocatalyst = False
        self.photocatalyst = photocatalyst

        self.scene_obj = []

        # Create a Material for pdms
        abs = Spectrum([0, 1000], [2, 2])
        # Giving emission suppress error. Not used due to quantum_efficiency = 0 :)
        ems = Spectrum([0, 1000], [0.1, 0])
        pdms = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.41)

        if name == '5x5_8ch':
            # 1. LSC DEVICE
            lsc = LSC(origin=(0,0,0), size=(0.050,0.050,3))
            # Clear reactor (control) is obtained with dye concentration = 0
            if dye == 'Red305':
                # Red305 absorption spectrum
                absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt'))
                # Wavelength at absorption peak
                ap = absorption_data[:, 1].max()
                # Linearity measured up to 0.15mg/g, to be measured beyond
                device_abs_at_peak = 13.023 * dye_concentration
                # Correcting factor to adjust absorption at peak to match settings
                device_transmission = 10 ** -device_abs_at_peak
                phi = -1 / (ap * 3 * np.log(device_transmission))
                # Applying correction to spectrum
                absorption_data[:, 1] = absorption_data[:, 1] * phi
                # Create Spectrum elements
                absorption = Spectrum(x=absorption_data[:, 0], y=absorption_data[:, 1])
                # fixme Add experimental data from pdms lo concentration samples (not reabsorption redshifted)
                emission_data = np.loadtxt(os.path.join(PVTDATA, "dyes", 'fluro-red-fit.ems.txt'))
                emission = Spectrum(x=emission_data[:, 0], y=emission_data[:, 1])
                # Create Material fixme Quantum Yield needs to be measured!
                fluro_red = Material(absorption_data=absorption, emission_data=emission, quantum_efficiency=0.95,
                                     refractive_index=1.41)
                lsc.material = CompositeMaterial([pdms, fluro_red], refractive_index=1.41, silent=True)
            else:
                raise Exception('Unknown dye! (',dye,')')
            lsc.name = 'Reactor (5x5cm, 8 channel, Dye: '+dye+')'
            self.scene_obj.append(lsc)

            # 2. CHANNELS
            reaction_mixture = self.getReactionMixture(solvent='acetonitrile')
            for i in range(1, 9):
                channel=Channel(origin=(0.005, 0.007 + 0.005*(i-1), 0.001), size=(0.040, 0.001, 0.001), shape="box")
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
        else:
            raise Exception('The reactor requested (',name,') is not known. Check the name ;)')

    def getReactionMixture(self, solvent=None):
        if solvent == None:
            n = 1.33
        elif solvent == 'acetonitrile':
            n = 1.344
        elif solvent == 'water':
            n = 1.33
        else:
            print "Unknown solvent. Water assumed as worst scenario (n=1.33)"
            n = 1.33

        if self.photocatalyst == "MB":
            # Open MB absorption
            mb_absorption_data = np.loadtxt(os.path.join(PVTDATA, "dyes", 'MB_abs.txt'))
            # Correction factor to adjust absoprtion to concentration, in M ** -1 (as in Materials.py:185)
            mb_phi = 100 * math.log(10) * 0.0004
            mb_absorption_data[:, 1] = mb_absorption_data[:, 1] * mb_phi
            # Giving emission suppress error. Not used due to quantum_efficiency = 0 :)
            ems = Spectrum([0, 1000], [0.1, 0])
            # Creates Spectrum
            mb_spectrum = Spectrum(x=mb_absorption_data[:, 0], y=mb_absorption_data[:, 1])
            reaction_mixture = Material(absorption_data=mb_spectrum, emission_data=ems, quantum_efficiency=0.0,
                                refractive_index=n)
            return reaction_mixture
        else:
            raise Exception('The photocatalyst (', self.reaction,') is unknown!')

class Statistics(object):
    """
    Class for analysis of results, based on the produced database.
    Can also be applied to old database data
    """

    def __init__(self, database):
        self.db = database
        self.photon_generated = len(self.db.uids_generated_photons())
        self.photon_killed = len(self.db.killed())
        self.tot = self.photon_generated-self.photon_killed
        self.non_radiative =  len(self.db.uids_nonradiative_losses())

    def percent(self, num_photons):
        """
        Return the percentage of num_photons with respect to thrown photons as 2 decimal digit string
        """
        return format((num_photons / self.tot)*100,'.2f')

    def print_report(self):
        print "##### PVTRACE LOG RESULTS #####"

        print "Summary:"
        print self.db.objects_with_records()
        #print "\t Photon efficiency \t", (luminescent_edges + luminescent_apertures) * 100 / thrown, "%"
        #print "\t Optical efficiency \t", luminescent_edges * 100 / thrown, "%"

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

        #print "Non radiative losses\t", self.percent(non_radiative_photons), "%"

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
            #print " ".join(map(str, self.db.wavelengthForUid(photon)))  # Clean output (for elaborations)

        print "Photons in channels (sum)", self.percent(photons_in_channels_tot), "% (", photons_in_channels_tot, ")"

        top_reflected = len(self.db.uids_out_bound_on_surface("top", solar=True))
        bottom_lost = len(self.db.uids_out_bound_on_surface("bottom", solar=True))

        #print thrown, "\t", top_reflected, "\t", bottom_lost, "\t", luminescent_edges, "\t", luminescent_apertures, "\t", (
        #photons_in_channels_tot - luminescent_photons_in_channels), "\t", luminescent_photons_in_channels, "\t", non_radiative_photons


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
        #print "Photons in channels array is: ",uid
        data = self.db.wavelengthForUid(uid)
        hist = np.histogram(data, bins=np.linspace(300,800,num=100))
        pylab.hist(data, 100, histtype='stepfilled')
        location = os.path.join(home,"pvtrace_export","plot-reactor.png")
        pylab.savefig(location)
        print 'Plot saved in ', location, '!'
        pylab.clf()

        print "Plotting reactor luminescent..."
        uid = db.uids_in_reactor_and_luminescent()
        #print "Photons in channels array is: ",uid
        data = db.wavelengthForUid(uid)
        hist = np.histogram(data, bins=np.linspace(300,800,num=100))
        pylab.hist(data, 100, histtype='stepfilled')
        location = os.path.join(home,"pvtrace_export","plot-reactor-luminescent.png")
        pylab.savefig(location)
        print 'Plot saved in ', location, '!'
        pylab.clf()
