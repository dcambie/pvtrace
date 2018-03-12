import logging
import numpy as np
import os
from pvtrace import *


class Photocatalyst(object):
    def __init__(self, compound, concentration):
        self.logger = logging.getLogger('pvtrace.photocat')
        self.logger.info('Photocat: "' + str(compound) + '", conc: ' + str(concentration))

        MB_list = ('MB', 'Methylene Blue', 'methylene blue', 'methyleneblue', 'methylene blauw', 'mb')
        eosin_list = ('Eosin', 'eosin', 'EY', 'Eosin Y', 'eosin y')
        rubpz_list = ('Ru(bpz)3', 'Rubpz', 'Ru(bpz)')
        # rubpy_list = ('Ru(bpy)3', 'Rubpy', 'Ru(bpy)')

        if compound in MB_list:
            self.compound = MethyleneBlue()
        elif compound in eosin_list:
            self.compound = EosinY()
        elif compound in rubpz_list:
            self.compound = Rubpz()
        # elif compound == 'Ru(bpy)3':
        #     self.compound = Rubpy()
        elif compound == 'Air':
            self.compound = Air()
        else:
            raise Exception('Unknown photocatalyst! (', compound, ')')
        self.concentration = concentration
        self.reaction_solvent = None

    def spectrum(self):
        # Get spectrum in absorption coefficient (m-1) for 1M compound
        photocat_abs_data = self.compound.abs()

        # Then adjust it based on molar concentration
        photocat_abs_data[:, 1] = photocat_abs_data[:, 1] * self.concentration
        return Spectrum(x=photocat_abs_data[:, 0], y=photocat_abs_data[:, 1])


class MethyleneBlue(object):
    @staticmethod
    def abs():
        # Load 1M Abs spectrum of MB. Values from http://omlc.org/spectra/mb/mb-water.html
        # To convert this data to absorption coefficient in (cm-1), multiply by the molar concentration and 2.303.
        # abs_data= np.loadtxt(os.path.join(PVTDATA, "dyes", 'MB_abs.txt'))
        # abs_data[:, 1] = abs_data[:, 1] * 100 * mat.log(10)
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'MB_1M_1m_ACN.txt'))


class EosinY(object):
    @staticmethod
    def abs():
        # Load 1M Abs spectrum of MB. Values from
        # return NotImplementedError
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'EY_1M_1m_EtOH_+base.txt'))


class Rubpz(object):
    @staticmethod
    def abs():
        # Load 1M Abs spectrum of MB. Values from
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'Ru(bpz)3_1M_1m_ACN.txt'))


class Air(object):
    """
    Air as photocatalyst: abs=0 for all wavelength.
    """

    @staticmethod
    def abs():
        # return Spectrum([0,1000], [0,0])
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'Air.txt'))

