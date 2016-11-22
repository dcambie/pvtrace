from pvtrace.Trace import Photon
import logging
from pvtrace.external.mathutils import vecDistance


class Trajectory(object):
    def __init__(self):
        self.steps = []
        self.logger = logging.getLogger("pvtrace.Trajectory")
    
    def add_step(self, position=None, direction=None, polarization=None, wavelength=None, active=False, container=None):
        photon = Photon(wavelength=wavelength, position=position, direction=direction, active=active)
        photon.polarisation = polarization
        photon.container = container
        self.steps.append(photon)
    
    def total_pathlength(self, subtract_first=True):
        """
        Calculate the total pathlength of a photon trajectory
        
        :param subtract_first: Removes first step from distance calculation. (That would typically be lamp to obj)
        :return: distance
        """
        previous = None
        distance = 0
        
        if subtract_first is True:
            first_element = 1
        else:
            first_element = 0
        for photon in self.steps[first_element:]:
            if previous is not None:
                distance += vecDistance(photon.getPosition(), previous.getPosition())
            previous = photon
        
        return distance
    
    def pathlength_per_obj(self):
        
        previous = None
        distance = 0
    
        for photon in self.steps[first_element:]:
            if previous is not None:
                distance += vecDistance(photon.getPosition(), previous.getPosition())
            previous = photon
    
        return distance
        pass