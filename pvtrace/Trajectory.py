from pvtrace.Trace import Photon
import logging
from pvtrace.external.mathutils import vecDistance


class Trajectory(object):
    def __init__(self):
        self.steps = []
        self.logger = logging.getLogger("pvtrace.Trajectory")
        self.known_obj = []
    
    def add_step(self, position=None, direction=None, polarization=None, wavelength=None, active=False, container=None,
                 on_surface_object=None):
        photon = Photon(wavelength=wavelength, position=position, direction=direction, active=active)
        photon.polarisation = polarization
        if str(container) not in self.known_obj:
            self.known_obj.append(str(container))
        photon.container = str(container)
        if str(on_surface_object) not in self.known_obj:
            self.known_obj.append(str(on_surface_object))
        photon.on_surface_object = str(on_surface_object)
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
        
        distance = []
        for obj in self.known_obj:
            distance.append((obj, 0))
        # print(str(self.known_obj))
        print(str(distance))
        
        for photon in self.steps[0:]:
            if previous is not None:
                current_distance = vecDistance(photon.getPosition(), previous.getPosition())
                if previous.container == photon.container:
                    i = [x for x in distance if photon.container in x][0]
                    distance[distance.index(i)] = (photon.container, distance[distance.index(i)][1]+current_distance)
                elif previous.container == photon.on_surface_object:
                    i = [x for x in distance if previous.container in x][0]
                    distance[distance.index(i)] = (previous.container, distance[distance.index(i)][1] + current_distance)
                else:
                    print(previous.container)
                #elif previous.container == "N"
                #    print(photon.container)
                #elif photon.container
                #if previous.container = photon.on_surface_object:
                #    distance[previous.container] = distance[previous.container] + current_distance
            previous = photon
        print(str(distance))
        pass