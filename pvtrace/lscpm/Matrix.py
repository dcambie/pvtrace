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
        elif matrix_name == 'PMMA' or matrix_name == 'pmma':
            self.polymer = PMMA()
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
    Class to generate spectra for PDMS-based devices
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
        # 0.5/m based on SI@ DOI: 10.1039/C0LC00707B
        return Spectrum([0, 1000], [0.5, 0.5])


class PMMA(object):
    """
    Class to generate spectra for PMMA-based devices
    """

    def __init__(self):
        self.name = 'Polymethylmethacrylate (PMMA)'
        self.logger = logging.getLogger('pvtrace.pmma')
        self.refractive_index = 1.4895

    @property
    def description(self):
        return self.name + ' (Limacryl)'

    def absorption(self):
        return Spectrum([0, 1100], [0.98, 0.98]) #final absorption coefficient determined by experiments
        # FIXME PMMA absorption coefficient is not plausiable in the near infrared region
        # PDMS absorption spectrum

        # 2/m based as in dfarrell code


        # return Spectrum(filename='D:\PvTrace_git\pvtrace-fork\data\pmma18.75.txt')
