from __future__ import division
import logging
from pvtrace import *
import numpy as np
import os


class LuminophoreMaterial(object):
    """
    Abstract class for LSC's dye material

    """
    def __init__(self, dye_name, concentration):
        if dye_name == 'Red305':
            self.dye = Red305(concentration/1000)
        else:
            raise Exception('Unknown dye! (', self.dye, ')')

    def name(self):
        return self.dye.name

    def description(self):
        return self.dye.description()

    def material(self):
        # Note that refractive index is not important here since it will be overwritten with CompositeMaterial's one
        return Material(absorption_data=self.dye.absorption(), emission_data=self.dye.emission(),
                        quantum_efficiency=self.dye.quantum_efficiency, refractive_index=1)


class Red305(object):
    """
    Class to generate spectra for Red305-based devices
    """

    def __init__(self, concentration):
        self.name = 'BASF Lumogen F Red 305'
        self.quantum_efficiency = 0.95
        self.concentration = concentration
        self.logger = logging.getLogger('pvtrace.red305')
        self.logger.info('concentration at red305 is  ' + str(concentration*1000) + ' ppm')

    def description(self):
        return self.name + ' (Concentration : ' + str(self.concentration) + 'mg/g)'

    def absorption(self):
        if self.concentration is None:
            raise Exception('Missing data for dye absorption. Concentration unknown')
        # Red305 absorption spectrum (reference at 0.10 mg/g)
        absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'Red305_010mg_g_1m-1.txt'))

        # Abs at 525 = 7.94956*dye loading
        # 1.0067 is the correction factor between exp. data at 0.10 mg/g and theoretical value
        phi = 1.006732182 * self.concentration/0.10
        self.logger.info('phi equals ' + str(phi) + ' (this should approximately be target concentration / 100 ppm')
        # Applying correction to spectrum
        absorption_data[:, 1] = absorption_data[:, 1] * phi

        return Spectrum(x=absorption_data[:, 0], y=absorption_data[:, 1])

    @staticmethod
    def emission():
        # fixme Add experimental data from pdms low concentration samples (not re-absorption red-shifted)
        emission_data = np.loadtxt(os.path.join(PVTDATA, "dyes", 'Red305_ems_spectrum.txt'))
        return Spectrum(x=emission_data[:, 0], y=emission_data[:, 1])
