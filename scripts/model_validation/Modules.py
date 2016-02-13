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

    def __init__(self, name, dye, device_abs_at_peak, photocatalyst=None):
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
            lsc = LSC(origin=(0,0,0), size=(50,50,3))
            # Clear reactor (control) is obtained with dye concentration = 0
            if dye == 'Red305':
                # Red305 absorption spectrum
                absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt'))
                # Wavelength at absorption peak
                ap = absorption_data[:, 1].max()
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
            lsc.name = "Reactor (5x5cm, 8 channel, Dye: ",dye,")"
            self.scene_obj.append(lsc)

            # 2. CHANNELS
            reaction_mixture = self.getReactionMixture(solvent='acetonitrile')
            for i in range(1, 8):
                channel=Channel(origin=(5, 7 + 5*(i-1), 1), size=(40, 1, 1), shape="box")
                channel.material = reaction_mixture
                channel.name = "Channel" + str(i)
                self.scene_obj.append(channel)
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