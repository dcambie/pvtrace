import logging

# In current implementation the class solvent is only used to set the refractive index of the reaction mixture.
# Solvents are considered transparent and the photocatalyst is the only absorbing specie in solution.
# Further improvement could be the introduction of the solvent spectra to account for the different cutoffs, with the
# corresponding code to split solvent and PC contributions to absorption (analogue to LSC matrix+dye)


class Solvent(object):
    """
    A DB of different solvents and their properties
    """

    def __init__(self, solvent_name="acetonitrile"):
        self.logger = logging.getLogger('pvtrace.solvent')

        # Data at 588nm (D-line sodium) from Burdick & Jackson + Wikipedia for some (ACN, DMSO, AcOEt, CHCl3)
        solvent_list = {(('acetonitrile', 'ACN', 'CH3CN'), 1.3441),#origin=1.3441
                        (('water', 'H2O'), 1.333),
                        (('Air', 'air'), 1.0),
                        (('N,N-DiMethylFormammide', 'dimethylformamide', 'DMF'), 1.4305),

                        # Alcohols
                        (('Methanol', 'Methyl alcohol', 'MeOH'), 1.3284),
                        (('Ethanol', 'Ethyl alcohol', 'EtOH'), 1.3614),
                        (('Isopropanol', 'Isopropyl alcohol', 'EtOH'), 1.3772),

                        # Ethers
                        (('Tetrahydrofuran', 'THF'), 1.4072),
                        (('Ethylether', 'Diethylether', 'Et2O'), 1.3524),
                        (('1,4-dioxane', 'Dioxane'), 1.4224),

                        # Alkanes
                        (('Hexane', 'Hex'), 1.3749),
                        (('Heptane', 'Hept'), 1.3876),

                        # Others
                        (('Acetone'), 1.3586),
                        (('EthylAcetate', 'AcOEt'), 1.3724),
                        (('Dichloromethane', 'Methylene chloride', 'DCM'), 1.4241),
                        (('Dimethylsulfoxide', 'DMSO'), 1.4793),
                        (('N-Methylpyrrolidone', 'NMP'), 1.4700),
                        (('Toluene', 'C6H5CH3'), 1.4969)}

        for solvent_tuple in solvent_list:
            if solvent_name in solvent_tuple[0]:
                self.n = solvent_tuple[1]
                self.logger.info('Solvent set to "' + str(solvent_name) + '" having a R.I. of '+str(self.n))

    def refractive_index(self):
        return self.n