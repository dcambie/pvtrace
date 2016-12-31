import logging
import numpy as np
import os
from pvtrace import *

class Photocatalyst(object):
    def __init__(self, compound, concentration):
        self.logger = logging.getLogger('pvtrace.photocat')
        self.logger.info('Photocat: "' + compound + '", conc: ' + str(concentration))

        if compound == 'MB':
            self.compound = MethyleneBlue()
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

        # FIXME: get peak and freq as max(photocat_abs_data)
        # peak = max(photocat_abs_data[:, 1])
        # wavelength = 0
        # self.logger.info('Calculated peak of absorption: ' + peak + ' at ' + wavelength + ' nm')
        return Spectrum(x=photocat_abs_data[:, 0], y=photocat_abs_data[:, 1])


class MethyleneBlue(object):
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

    @staticmethod
    def abs():
        # return Spectrum([0,1000], [0,0])
        return np.loadtxt(os.path.join(PVTDATA, "photocatalysts", 'Air.txt'))
