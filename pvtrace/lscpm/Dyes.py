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
        elif dye_name == 'K160':
            self.dye = K160()
        elif dye_name == 'Evonik_Blue':
            self.dye = Blue_5C50()
        elif dye_name == 'Evonik_lr305':
            self.dye = Evonik_lr305()
        elif dye_name == 'Limacryl_lr305':
            self.dye = Limacryl_lr305()
        else:
            raise NotImplementedError('Unknown dye! (', self.dye, ')')

    def name(self):
        return self.dye.name

    def description(self):
        return self.dye.description()

    def material(self):
        # Note that refractive index is not important here since it will be overwritten with CompositeMaterial's one
        return Material(absorption_data=self.dye.absorption(), emission_data=self.dye.emission(),
                        quantum_efficiency=self.dye.quantum_efficiency, refractive_index=1)


class Red305(LuminophoreMaterial):
    """
    Class to generate spectra for Red305-based devices
    """

    def __init__(self, concentration):
        self.name = 'BASF Lumogen F Red 305'
        self.quantum_efficiency = 0.95
        self.concentration = concentration
        self.logger = logging.getLogger('pvtrace.red305')
        self.logger.info('concentration of red305 is  ' + str(concentration*1000) + ' ppm')

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
        return Spectrum(filename=os.path.join(PVTDATA, "dyes", 'Red305_ems_spectrum.txt'))


class K160(LuminophoreMaterial):
    """
    Class to generate spectra for K160-based devices
    """

    def __init__(self):
        self.name = 'Yellow Risk Reactor DFSB-K160'
        self.quantum_efficiency = 0.95  # FIXME Literature search for this needed
        self.logger = logging.getLogger('pvtrace.k160')
        self.logger.info(self.description)

    def description(self):
        return self.name

    def absorption(self):
        # K160 absorption spectrum (from Limacryl custom-made PMMA sample)
        return Spectrum(filename=os.path.join(PVTDATA, 'dyes', 'K160_Limacryl_4mm_normalized_to_1m.txt'))

    def emission(self):
        return Spectrum(filename=os.path.join(PVTDATA, "dyes", 'K160_ems.txt'))


class Blue_5C50(LuminophoreMaterial):
    """
    Class to generate spectra for Evonik Blue 5C50-based LSC
    """

    def __init__(self):
        self.name = 'Plexiglas Fluorescent Blue 5C50'
        self.quantum_efficiency = 0.95  # FIXME Literature search for this needed
        self.logger = logging.getLogger('pvtrace.blue')
        self.logger.info(self.description())

    def description(self):
        return self.name

    def absorption(self):
        # Blue LSC absorption spectrum
        # absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'Evonik_blue_5C50_abs.txt'))
        return Spectrum(filename=os.path.join(PVTDATA, 'dyes', 'Evonik_blue_5C50_abs.txt'))

    def emission(self):
        return Spectrum(filename=os.path.join(PVTDATA, "dyes", 'Evonik_blue_5C50_ems.txt'))


class Evonik_lr305(LuminophoreMaterial):
    """
    Class to generate spectra for Evonik Blue 5C50-based LSC
    """

    def __init__(self):
        self.name = 'Evonik_lr305 based on PMMA'
        self.quantum_efficiency = 0.95  # FIXME Literature search for this needed
        self.logger = logging.getLogger('pvtrace.red')
        self.logger.info(self.description())

    def description(self):
        return self.name

    def absorption(self):
        # Blue LSC absorption spectrum
        # absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'Evonik_blue_5C50_abs.txt'))
        return Spectrum(filename=os.path.join(PVTDATA, 'dyes', 'Evonik_lr305_normalized_to_1m.txt'))

    def emission(self):
        return Spectrum(filename=os.path.join(PVTDATA, "dyes", 'Evonik_lr305_normalized_to_1m_ems.txt'))


class Limacryl_lr305(LuminophoreMaterial):
    """
    Class to generate spectra for Evonik Blue 5C50-based LSC
    """

    def __init__(self):
        self.name = 'Plexiglas Fluorescent Blue 5C50'
        self.quantum_efficiency = 0.95  # FIXME Literature search for this needed
        self.logger = logging.getLogger('pvtrace.blue')
        self.logger.info(self.description())

    def description(self):
        return self.name

    def absorption(self):
        # Blue LSC absorption spectrum
        # absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'Evonik_blue_5C50_abs.txt'))
        return Spectrum(filename=os.path.join(PVTDATA, 'dyes', 'Limacryl_lr305_normalized_to_1m.txt'))

    def emission(self):
        return Spectrum(filename=os.path.join(PVTDATA, "dyes", 'Limacryl_lr305_normalized_to_1m_ems.txt'))