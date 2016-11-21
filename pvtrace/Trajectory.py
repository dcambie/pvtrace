from pvtrace.Trace import Photon


class Trajectory(object):
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, position=None, direction=None, polarization=None, wavelength=None, active=False, container=None):
        photon = Photon(wavelength=wavelength, position=position, direction=direction, active=active)
        photon.polarisation = polarization
        photon.container = container
        self.steps.append(photon)