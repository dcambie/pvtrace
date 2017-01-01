import logging
from pvtrace import *
import numpy as np
import os


class Matrix(object):
    """
    Abstract class for LSC's matrix
    """
    def __init__(self, matrix_name):
        if matrix_name == 'PDMS' or matrix_name == 'pdms':
            self.polymer = PDMS()
        else:
            raise Exception('Unknown dye! (', self.dye, ')')

    def name(self):
        return self.polymer.name

    def description(self):
        return self.polymer.description

    def refractive_index(self):
        return self.polymer.refractive_index

    def material(self):
        ems = Spectrum([0, 1000], [0.1, 0])
        # Note that refractive index is not important here since it will be overwritten with CompositeMaterial's one
        return Material(absorption_data=self.polymer.absorption(), emission_data=ems,
                        quantum_efficiency=0, refractive_index=1)


class PDMS(object):
    """
    Class to generate spectra for Red305-based devices
    """

    def __init__(self):
        self.name = 'Polydimethylsiloxane (PDMS)'
        self.logger = logging.getLogger('pvtrace.pdms')
        self.refractive_index = 1.4118

    @property
    def description(self):
        return self.name + ' (Dow-Corning Sylgard 184)'

    def absorption(self):
        # PDMS absorption spectrum
        absorption_data = np.loadtxt(os.path.join(PVTDATA, 'PDMS.txt'))

        return Spectrum(x=absorption_data[:, 0], y=absorption_data[:, 1])
