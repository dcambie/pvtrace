# pvtrace is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# pvtrace is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import warnings
import logging
import math
from pvtrace.external.transformations import rotation_matrix
import pvtrace.external.transformations as tf

from pvtrace.Materials import *


class Register(object):
    """
    A class that will register photon position and wavelength. Device objects are subclasses of register.
    """

    def __init__(self):
        super(Register, self).__init__()
        self.store = dict()
        # Dictionary whose keys are surface_identifiers. The items are
        # arrays where each index is a tuple containing ray statistics
        # as indicated in self.log()
        self.logger = logging.getLogger('pvtrace.devices')

    def log(self, photon):
        # Need to check that the photon is on the surface
        if not self.shape.on_surface(photon.position):

            if not photon.active:
                # The photon has been non-radiatively lost inside a material
                key = 'loss'
                if key not in self.store:
                    self.store[key] = []

                log_entry = (list(photon.position), float(photon.wavelength), None, photon.absorption_counter)
                self.store[key].append(log_entry)
                self.logger.debug('Photon lost')
                return
            else:
                # A photon has been logged in the interior of a material but photon.active = True, which means it is not
                # non-radiatively lost. So why is it being logged?"
                warnings.warn("It is likely that a light source has been placed inside an object."
                              "The light source should be external. Now attempting to log the ray and continue.")
                self.logger.warn("Active photon logged within material. Likely to be an error caused by a lightsource"
                                 "placed within the material")

                key = 'volume_source'
                if key not in self.store:
                    self.store[key] = []
                log_entry = (list(photon.position), float(photon.wavelength), None, photon.absorption_counter)
                self.store['volume_source'].append(log_entry)
                self.logger.debug("Logged as photon from a volume source")
                return

        # Can do this because all surface_normal with the acute flag False returns outwards facing normals.
        normal = photon.exit_device.shape.surface_normal(photon.ray, acute=False)
        rads = angle(normal, photon.ray.direction)

        # If the angle between ray direction and normal is less than pi/2 than outbond, inbound otherwise
        bound = "outbound" if rads < (np.pi / 2) else "inbound"
        self.logger.debug("Photon logged as " + bound)

        key = photon.exit_device.shape.surface_identifier(photon.position)
        if key not in self.store:
            self.store[key] = []

        # [0] --> position
        # [1] --> wavelength
        # [2] --> surface side (inbound or outbound)
        # [3] --> re-absorptions
        # [4] --> total jumps
        # [5] --> object_number
        log_entry = (list(photon.position), float(photon.wavelength), bound, photon.absorption_counter)
        self.store[key].append(log_entry)

    def print_store(self):
        print(self.store)

    def count(self, shape, surface_point, bound):
        """
        Returns the number of photon counts that are on the 
        same surface as the surface_point for the given shape.
        """

        key = shape.surface_identifier(surface_point)
        if key not in self.store:
            return 0.0
        entries = self.store[key]
        counts = 0
        for entry in entries:
            if entry[2] == bound:
                counts += 1

        if counts is None:
            return 0
        return counts

    def count_face(self, face_name):
        """
        Returns the number of photon counts that are on the
        same surface as the surface_point for the given shape.
        """
        entries = []
        if face_name in self.store:
            entries += self.store[face_name]
        else:
            return 0.0

        counts = len(entries)
        if counts == 0:
            return 0.0
        return counts

    def loss(self):
        """
        Returns the number of photons that have been non-radiatively lost in the volume of the shape. 
        A more adventurous version of this could be made that returns positions. 
        """
        if 'loss' not in self.store:
            return 0
        return len(self.store['loss'])

    def spectrum_face(self, surface_names=()):
        """
        Returns the counts histogram (bins,counts) for object
        """
        wavelengths = []

        entries = []
        for surface in surface_names:
            if surface in self.store:
                entries += self.store[surface]

        if len(entries) == 0:
            return None

        for entry in entries:
            wavelengths.append(float(entry[1]))

        if len(wavelengths) is 0:
            return None

        wavelengths = np.array(wavelengths)

        if len(wavelengths) is 1:
            bins = np.arange(np.floor(wavelengths[0] - 1), np.ceil(wavelengths[0] + 2))
            freq, bins = np.histogram(wavelengths, bins=bins)
        else:
            bins = np.arange(np.floor(wavelengths.min() - 1), np.ceil(wavelengths.max() + 2))
            freq, bins = np.histogram(wavelengths, bins=bins)
        return Spectrum(bins[0:-1], freq)

    def spectrum(self, shape, surface_point, bound):
        """
        Returns the counts histogram (bins,counts) for object
        """
        wavelengths = []
        key = shape.surface_identifier(surface_point)
        if key not in self.store:
            return None

        entries = self.store[key]
        if len(entries) == 0:
            return None

        for entry in entries:
            if entry[2] == bound:
                wavelengths.append(float(entry[1]))

        if len(wavelengths) is 0:
            return None

        wavelengths = np.array(wavelengths)

        if len(wavelengths) is 1:
            bins = np.arange(np.floor(wavelengths[0] - 1), np.ceil(wavelengths[0] + 2))
            freq, bins = np.histogram(wavelengths, bins=bins)
        else:
            bins = np.arange(np.floor(wavelengths.min() - 1), np.ceil(wavelengths.max() + 2))
            freq, bins = np.histogram(wavelengths, bins=bins)
        return Spectrum(bins[0:-1], freq)

    def reabs(self,surface_names=()):
        """
        16/03/10: Returns list where list[i+1] contains number of surface photons that experienced i re-absorptions;
        Length of list is ten by default (=> photons with up to 9 re-absorptions recorded), but is extended if necessary
        """

        entries = []
        for surface in surface_names:
            if surface in self.store:
                entries += self.store[surface]

        if len(entries) == 0:
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        reabs_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for entry in entries:

            number_reabs = entry[3]

            # In case reabs_list is not sufficiently long...
            if number_reabs + 1 > len(reabs_list):
                while len(reabs_list) < number_reabs + 1:
                    reabs_list.append(0)

            reabs_list[number_reabs] += 1

        return reabs_list

    def loss_reabs(self):
        """
        16/03/10: Returns list where list[i+1] contains number of LOST photons that experienced i re-absorptions;
        Length of list is ten by default (=> photons with up to 9 re-absorptions recorded), but is extended if necessary
        """

        if 'loss' not in self.store:
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        reabs_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        loss_entries = self.store['loss']

        for entry in loss_entries:

            number_reabs = entry[3]

            if number_reabs + 1 > len(reabs_list):
                while len(reabs_list) < number_reabs + 1:
                    reabs_list.append(0)

            reabs_list[number_reabs] += 1

        return reabs_list


class Detector(Register):
    """
    An abstract class to base solar cell like object from.

    Similar to the register class but will deactivate photon when hit.
    """

    def __init__(self):
        super(Detector, self).__init__()


class SimpleCell(Detector):
    """
    A SimpleCell object is a solar cell with perfect AR coating.
    """

    def __init__(self,  finiteplane, origin=(0., 0., 0.,)):
        super(Detector, self).__init__()
        self.shape = finiteplane
        self.shape.append_transform(tf.translation_matrix(origin))
        self.name = "cell"
        self.material = None


class Coating(Register):
    """
    Overview:
    A coating device is a shape that contains a reflective material which may
    have an spectral and angular dependent reflectivity.

    Details:
    When a ray hits an object, the Fresnel equation are used to determine if
    the ray continues on it's path or is reflected. Coatings are special
    objects that supply there own reflectivity, and may also define
    Rather than using Fresnel equation to determine the reflectivity of
    """

    # Todo CD 21/03/16: If needed uncomment the relative code in Trace

    def __init__(self, reflectivity, shape, refractive_index=1., lambertian=False):
        super(Coating, self).__init__()
        self.name = "COATING"
        self.shape = shape
        self.refractive_index = refractive_index
        self.reflectivity = ReflectiveMaterial(reflectivity, refractive_index=refractive_index, lambertian=lambertian)
        self.material = SimpleMaterial(555)  # This create a material with absorption_coefficient = 0.
        if not isinstance(self.shape, Polygon):
            self.origin = self.shape.origin
            self.size = np.abs(self.shape.extent - self.shape.origin)


class Bounds(Register):
    """
    A huge box containing only air with refractive index 1.
    """

    def __init__(self):
        super(Bounds, self).__init__()
        # self.shape = Box(origin=(-0.1, -0.1, -0.1), extent=(2, 2, 2))
        # self.shape = Box(origin=(-1, -1, -1), extent=(20, 20, 20))
        self.shape = Box(origin=(-1, -1, -1), extent=(3, 3, 3))
        self.material = Material()
        self.name = "BOUNDS"


class Rod(Register):
    """docstring for Rod"""

    def __init__(self, bandgap=555, radius=1, length=1):
        super(Rod, self).__init__()
        self.shape = Cylinder(radius, length)
        self.material = SimpleMaterial(bandgap)


class Prism(Register):
    """Prism"""

    def __init__(self, bandgap=555, base=1, alpha=np.pi / 3, beta=np.pi / 3, length=1):
        super(Prism, self).__init__()
        h = base * (1 / np.tan(alpha) + 1 / np.tan(alpha))
        box0 = Box(origin=(0, 0, 0), extent=(base, h, length))
        box1 = Box(origin=(0, 0, 0), extent=(h / np.sin(alpha), h, length))
        box1.append_transform(tf.rotation_matrix(alpha, (0, 0, 1)))
        box2 = Box(origin=(base, 0, 0), extent=(base + h, h / np.sin(beta), h, length))
        box2.append_transform(tf.rotation_matrix(np.pi / 2 - beta, (0, 0, 1)))
        step1 = CSGsub(box0, box1)
        step2 = CSGsub(step1, box2)
        self.shape = step2
        self.material = SimpleMaterial(bandgap)


class LSC(Register):
    """LSC implementation."""

    def __init__(self, bandgap=555, origin=(0, 0, 0), size=(1, 1, 1)):
        super(LSC, self).__init__()
        self.origin = np.array(origin)
        self.size = np.array(size)
        self.shape = Box(origin=origin, extent=np.array(origin) + np.array(size))
        self.material = SimpleMaterial(bandgap)
        self.name = "LSC"

        """
        16/03/10: Assume that surfaces with a solar cell attached are index matched. This makes
        sure that all surfaces that hit one of the collection edges are counted.
        e.g. index_matched_surfaces = ['top', 'bottom']
        """
        self.index_matched_surfaces = []


# class Tubing(Register):
#     """Tubing of a capillary, e.g. PFA, or FEP, usually 1/16" OD, hosts a Channel object"""
#
#     def __init__(self, bandgap=555, origin=(0, 0, 0), size=(1, 1, 1)):
#         self.origin = np.array(origin)
#         self.size = np.array(size)
#         # The following is a little workaround to convert origin, size into cylinder (radius, length) descriptors
#         # Axis is based on the longest direction among the size (x,y,z)
#         axis = np.argmax(size)
#         # Length is the value of the longest axis of size
#         length = np.amax(size)
#         # Radius is the average of the other two coordinates
#         radius = np.average(np.delete(size, axis))
#         self.shape = Cylinder(radius=radius, length=length)
#
#         # For CSG first rotation then translation (assuming scaling is not needed)
#         if axis == 0:  # Z to X Rotation needed
#             self.shape.append_transform(tf.rotation_matrix(math.pi / 2.0, [0, 1, 0]))
#         elif axis == 1:  # Z to Y Rotation needed
#             self.shape.append_transform(tf.rotation_matrix(-math.pi / 2.0, [1, 0, 0]))
#
#         self.shape.append_transform(tf.translation_matrix(origin))

class Channel(Register):
    """Liquid in reactor's channel simulation"""

    def __init__(self, bandgap=555, origin=(0, 0, 0), size=(1, 1, 1), shape="box"):
        super(Channel, self).__init__()
        self.origin = np.array(origin)
        self.size = np.array(size)
        self.volume = 1
        if shape == "box":
            self.shape = Box(origin=origin, extent=np.array(origin) + np.array(size))
            for coord in size:
                self.volume *= coord
        elif shape == "cylinder":  # takes radius, length
            # The following is a little workaround to convert origin, size into cylinder (radius, length) descriptors
            # Axis is based on the longest direction among the size (x,y,z)
            axis = np.argmax(size)
            # Length is the value of the longest axis of size
            length = np.amax(size)
            # Radius is the average of the other two coordinates
            radius = np.average(np.delete(size, axis))

            # Cylinder volume formula
            self.volume = math.pi * radius ** 2 * length

            self.shape = Cylinder(radius=radius, length=length)

            # For CSG first rotation then translation (assuming scaling is not needed)
            if axis == 0:  # Z to X Rotation needed
                self.shape.append_transform(tf.rotation_matrix(math.pi / 2.0, [0, 1, 0]))
            elif axis == 1:  # Z to Y Rotation needed
                self.shape.append_transform(tf.rotation_matrix(-math.pi / 2.0, [1, 0, 0]))

            self.shape.append_transform(tf.translation_matrix(origin))
        else:
            self.logger.warn("The channel shape is invalid (neither box nor cylinder. It was " + str(shape))
            raise Exception("Channel has invalid shape")
        self.material = SimpleMaterial(bandgap)
        self.name = "Channel"


# class Collector(Register):
#    """Collector implementation."""
#    def __init__(self, bandgap=555, origin=(0,0,0), size=(1,1,1)):
#        super(Collector, self).__init__()
#        self.origin = np.array(origin)
#        self.size = np.array(size)
#        self.shape = Box(origin=origin, extent=np.array(origin) + np.array(size))
#        self.material = SimpleMaterial(bandgap)
#        self.name = "LSC"

class RayBin(Register):
    """An class for erasing the ray if it hits this device. --> e.g. a solar cell!"""

    def __init__(self, bandgap=555, origin=(0, 0, 0), size=(1, 1, 1)):
        super(RayBin, self).__init__()
        self.origin = np.array(origin)
        self.size = np.array(size)
        self.shape = Box(origin=origin, extent=np.array(origin) + np.array(size))
        # import pdb; pdb.set_trace()
        self.material = SimpleMaterial(bandgap)
        self.name = "RayBin"


class PlanarMirror(Register):
    """Planar mirror with variable reflectivity (constant or wavelength dependent but constant in angle). """

    def __init__(self, reflectivity=1.0, origin=(0, 0, 0), size=(1, 1, 0.001)):
        super(PlanarMirror, self).__init__()
        self.reflectivity = reflectivity
        self.shape = Box(origin=np.array(origin), extent=np.array(origin) + np.array(size))
        self.material = ReflectiveMaterial(reflectivity)


class PlanarReflector(Register):
    """Planar reflector with variable reflectivity (constant or wavelength dependent but constant in angle). """

    def __init__(self, reflectivity=1.0, origin=(0, 0, 0), size=(1, 1, 0.001)):
        super(PlanarReflector, self).__init__()
        self.reflectivity = reflectivity
        self.shape = Box(origin=np.array(origin), extent=np.array(origin) + np.array(size))
        self.material = ReflectiveMaterial(reflectivity=reflectivity, refractive_index=1, lambertian=True)


class Face(Register):
    """General 2D object for ray tracing surfaces."""

    def __init__(self, reflectivity=1.0, transmittance=-1, shape=Polygon([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])):
        super(Face, self).__init__()
        assert reflectivity + transmittance < 1, "reflectivity + transmittance of Face device must be smaller than 1.0"
        self.reflectivity = reflectivity
        # if reflectivity -> ray reflected, if transmittance -> ray goes straight through, else: ray lost
        if transmittance < 0:
            self.transmittance = 1 - self.reflectivity
        else:
            self.transmittance = transmittance
        self.shape = shape
        self.material = None
        self.name = "FACE"
