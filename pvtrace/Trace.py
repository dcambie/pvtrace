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

from __future__ import division, print_function

import subprocess
import os
import time
import sys
from copy import copy

import shortuuid
import logging

import pvtrace.Analysis
import pvtrace.PhotonDatabase
import pvtrace.Scene
from pvtrace.Devices import *


try:
    import visual
    from Visualise import Visualiser
except Exception:
    pass

# import multiprocessing
# cpu_count = multiprocessing.cpu_count()


def remove_duplicates(the_list):
    l = list(the_list)
    return [x for x in l if l.count(x) == 1]


def file_opener(file_path):
    """
    Opens a give file with the system default application

    :param file_path: File to be open
    :return:
    """
    if os.name == 'nt':
        os.startfile(file_path)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', file_path))
    elif sys.platform.startswith('darwin'):
        subprocess.call(('open', file_path))
    else:
        assert "unknown platform!"


class Photon(object):
    """
    A generic photon class.
    """

    def __init__(self, wavelength=555, position=None, direction=None, active=True):
        """
        Initialize the photon.

        All arguments are optional because a photon is created with default values.
        :param wavelength: the photon wavelength in nanometers (float).
        :param position: the photon position in cartesian coordinates is an array-like quantity in units of metres
        :param direction: the photon Cartesian direction vector (3 elements), a normalised vector is array-like
        :param active: boolean indicating if the ray has or has not been lost (e.g. absorbed in a material)

        >>> a = Photon()
        >>> a.wavelength
        555
        >>> a.position
        array([ 0.,  0.,  0.])
        >>> a.direction
        array([ 0.,  0.,  1.])
        >>> a.active
        True
        >>> a.wavelength = 600
        >>> b = a
        >>> b.wavelength
        600
        >>> a.ray
        <pvtrace.Geometry.Ray object at ...
        >>> print(a) # This will fail in Python 3 as <class 'NoneType'> is returned
        600nm [ 0.  0.  0.] [ 0.  0.  1.] <type 'NoneType'> active
        """

        if position is not None:
            position = np.array(position)
        if direction is not None:
            direction = np.array(direction)
        # Note that Ray can correctly handle None as arguments, but not NoneType (result of np.array(None))
        self.ray = Ray(position, direction)

        self.wavelength = wavelength
        self.active = active
        self.killed = False
        self.container = None
        self.exit_material = None
        self.exit_device = None
        self.__direction = self.ray.direction
        self.__position = self.ray.position
        self.scene = None
        self.propagate = False
        self.visualiser = None
        self.polarisation = None
        self.absorber_material = None
        self.emitter_material = None
        self.on_surface_object = None
        self.reabs = 0
        self.id = 0
        self.source = None
        self.absorption_counter = 0
        self.intersection_counter = 0
        self.reaction = False
        self.previous_container = None
        self.visual_obj = []
        self.log = logging.getLogger("pvtrace.Photon")

    def __copy__(self):
        photon_copy = Photon()
        photon_copy.wavelength = self.wavelength
        photon_copy.ray = Ray(direction=self.direction, position=self.position)
        photon_copy.active = self.active
        photon_copy.container = self.container
        photon_copy.exit_material = self.exit_material
        photon_copy.exit_device = self.exit_device
        photon_copy.scene = self.scene
        photon_copy.propagate = self.propagate
        photon_copy.visualiser = self.visualiser
        photon_copy.absorption_counter = self.absorption_counter
        photon_copy.intersection_counter = self.intersection_counter
        photon_copy.polarisation = self.polarisation
        photon_copy.reabs = self.reabs
        photon_copy.id = self.id
        photon_copy.source = self.source
        photon_copy.absorber_material = self.absorber_material
        photon_copy.emitter_material = self.emitter_material
        photon_copy.on_surface_object = self.on_surface_object
        photon_copy.reaction = self.reaction
        photon_copy.visual_obj = self.visual_obj
        return photon_copy

    def __deepcopy__(self):
        return copy(self)

    def __str__(self):
        info = str(self.wavelength) + "nm " + str(self.ray.position) + " " + str(self.ray.direction) + " " + str(
            type(self.container))
        if self.active:
            info += " active "
        else:
            info += " inactive "
        return info

    def is_reaction(self):
        """
        True if the photon path ends in the reaction mixture
        """
        return self.reaction

    def getPosition(self):
        """
        Returns the position of the photons rays
        """
        return self.ray.position

    def setPosition(self, position):
        self.ray.position = position
        # Define setter and getters as properties

    position = property(getPosition, setPosition)

    def getDirection(self):
        """
        Returns the direction of the photons rays
        """
        return self.ray.direction

    def setDirection(self, direction):
        self.ray.direction = direction

    direction = property(getDirection, setDirection)

    def trace(self):
        """
        The ray can trace itself through the scene.
        """

        assert self.scene is not None, "The photon's scene variable is not set."

        intersection_points, intersection_objects = self.scene.intersection(self.ray)

        assert intersection_points is not None, "The ray must intersect with something in the scene to be traced."

        if self.container is None:
            self.container = self.scene.container(self)
        assert self.container is not None, "Container of ray cannot be found."

        # import pdb; pdb.set_trace()
        intersection_points, intersection_objects = self.scene.sort(intersection_points, intersection_objects, self,
                                                                    container=self.container)

        # find current intersection point and object -- should be zero if the list is sorted!
        intersection = closest_point(self.position, intersection_points)
        for i in range(0, len(intersection_points)):
            if list(intersection_points[i]) == list(intersection):
                index = i
                break

        intersection_object = intersection_objects[index]
        assert intersection_object is not None, "No intersection points can be found with the scene."

        # Reached scene boundaries?
        if intersection_object is self.scene.bounds:
            self.active = False
            self.previous_container = self.container
            self.container = intersection_object
            return self

            # Reached a RayBin (kind of perfect absorber)?
        if isinstance(intersection_object, RayBin):
            self.active = False
            self.previous_container = self.container
            self.container = intersection_object
            return self
        
        # reached a SimpleCell - absorbs everything.
        if isinstance(intersection_object, SimpleCell):
            self.active = False
            self.previous_container = self.container
            self.container = intersection_object
            return self

        # Here we trace the ray through a Coating
        # if isinstance(self.container, Coating):
        #    if self.container.material.lambertian:
        #        # If a lambertian coating we need the normal to the hemisphere that light will be reflected into
        #        normal = intersection_object.shape.surface_normal(self.ray, acute=False)
        #    else:
        #        normal = intersection_object.shape.surface_normal(self.ray)
        #    
        #    # For the coating the normal must be facing the ray
        #    self = self.container.material.trace(self, normal, separation(self.position, intersection))
        #    self.exit_device = self.container
        #    self.previous_container = self.container
        #    self.container = self.scene.container(self)
        #    return self

        # Here we determine if the Coating has been hit
        # if isinstance(intersection_object, Coating) and intersection_object.shape.on_surface(self.position):
        #    self.previous_container = self.container
        #    self.container = intersection_object
        #    self.exit_device = intersection_object
        #    assert self.exit_device != self.scene.bounds, "The object the ray hit before hitting the bounds
        #                                                   is the bounds itself, this can't be right."
        #    return self

        # Here we trace the ray through a Material
        self.container.material.trace(self, separation(self.position, intersection))

        # Lost in material?
        # Photon has been re-absorbed but NOT re-emitted, i.e. is inactive
        if not self.active:
            # 01/04/10: Unification --> Next two lines came from older Trace version
            self.exit_device = self.container
            self.exit_material = self.container.material
            self.on_surface_object = None  # Impossible to be non-radiatively lost by a surface

            # If photon ends up in a channel then set reaction to true! [D.]
            if isinstance(self.container, Channel):
                self.reaction = True
            return self

        # Reaches interface
        # Photon has been re-absorbed AND re-emitted, i.e. is still active
        ray_on_surface = intersection_object.shape.on_surface(self.position)
        if not ray_on_surface and self.active:
            self.exit_device = self.container
            self.on_surface_object = None
            return self

        # Ray has reached a surface of some description, set some state variables
        self.on_surface_object = intersection_object
        self.intersection_counter += 1

        # edge = False
        # if ray_on_surface and isinstance(intersection_object, LSC) and isinstance(self.container, LSC)
        #       and self.container.shape.surface_identifier(self.position) in edges:
        #     edge = self.container.shape.surface_identifier(self.position)

        # If we reach an reflective material then we don't need to follow
        # this logic we can just return
        # if ray_on_surface and isinstance(intersection_object, Coating):
        #    self.previous_container = self.container
        #    self.container = intersection_object
        #    self.exit_device = intersection_object
        #    return self

        # KARLG NEW CODE HERE
        # import pudb; pudb.set_trace()
        if isinstance(intersection_object, Face):
            self.exit_device = intersection_object
            print("FACE EXISTS")

            # Now change the properties of the photon according to what your surface does
            random_number = np.random.random_sample()
            if random_number < intersection_object.reflectivity:
                # Reflected
                self.direction = reflect_vector(intersection_object.shape.surface_normal(self.ray), self.direction)
            elif random_number < intersection_object.reflectivity + intersection_object.transmittance:
                # Transmitted
                pass
            else:
                # Loss
                self.active = False
            return self

        # material-air or material-material interface
        # Are there duplicates intersection_points that are equal to the ray position?
        same_pt_indices = []
        for i in range(0, len(intersection_points)):
            if cmp_points(self.position, intersection_points[i]):
                same_pt_indices.append(i)
        assert len(same_pt_indices) < 3, "An interface can only have 2 or 0 common intersection points."

        if len(same_pt_indices) == 2:
            intersection_object = self.container

        #
        # Calculate the reflectivity of surface
        #

        # Reflection and refraction require the surface normal
        normal = intersection_object.shape.surface_normal(self.ray)
        rads = angle(normal, self.direction)

        # Hit order: from inside or outside?
        if self.container == intersection_object:

            # hitting internal interface
            initialised_internally = True

            if len(same_pt_indices) == 2:
                # Internal interface for the case for 2 material-material interfaces which are touching
                # (i.e. not travelling through air)
                for obj in intersection_objects:
                    if obj.shape.on_surface(intersection) and obj != self.container:
                        next_containing_object = obj
            else:
                # hitting internal interface -- for the case where the boundary materials are NOT touching
                # (i.e. we are leaving an material embedded in another)
                next_containing_object = self.scene.container(self)

            assert self.container != next_containing_object, "The current container cannot also be the next" \
                                                             "containing object after the ray is propagated."

            # Calculate interface reflectivity
            if isinstance(intersection_object, Coating):
                # CONVENTION: The internal reflectivity of Coating objects is zero. 
                # This avoids multiple reflections within these structures.
                # reflection = intersection_object.reflectivity(self)
                reflection = 0.
            elif isinstance(intersection_object, PlanarReflector):
                reflection = 0.
            elif isinstance(next_containing_object, Coating):
                # Catches the case when a Coating is touching an interface, forcing it to use the Coatings 
                # reflectivity rather than standard Fresnel reflection
                reflection = next_containing_object.reflectivity(self)
            else:
                # Fresnel reflection
                if self.polarisation is None:
                    reflection = fresnel_reflection(rads, self.container.material.refractive_index,
                                                    next_containing_object.material.refractive_index)
                else:
                    reflection = fresnel_reflection_with_polarisation(normal, self.direction, self.polarisation,
                                                                      self.container.material.refractive_index,
                                                                      next_containing_object.material.refractive_index)

        else:
            # hitting external interface
            initialised_internally = False

            if len(same_pt_indices) == 2:
                # External interface which are touching (i.e. not travelling through air)
                for obj in intersection_objects:
                    if obj != self.container:
                        intersection_object = obj
                        next_containing_object = obj
            else:
                # External interfaces NOT touching (i.e. travelling through air)
                next_containing_object = intersection_object

            # Calculate interface reflectivity
            if isinstance(intersection_object, Coating):
                # Coating has special reflectivity
                reflection = intersection_object.reflectivity(self)
            elif isinstance(intersection_object, PlanarReflector):
                reflection = intersection_object.material(self)
            else:
                # Fresnel reflection
                if self.polarisation is None:
                    reflection = fresnel_reflection(rads, self.container.material.refractive_index,
                                                    next_containing_object.material.refractive_index)
                else:
                    reflection = fresnel_reflection_with_polarisation(normal, self.direction, self.polarisation,
                                                                      self.container.material.refractive_index,
                                                                      next_containing_object.material.refractive_index)

        #
        # Does reflection or refraction occur?
        #

        if np.random.uniform() < reflection:
            # Reflection occurs

            #            if isinstance(intersection_object, Channel):
            #                super().reflected += 1
            #                print "Photon was reflected by channel :("
            #

            # Cache old direction for later use by polarisation code
            old_direction = copy(self.direction)

            # Handle PlanarReflector
            if isinstance(intersection_object, PlanarReflector):
                self.direction = intersection_object.material.reflected_direction(self, normal)
                self.propagate = False
                self.exit_device = self.container
                return self

            if isinstance(intersection_object, Coating):
                # Coating reflection (can be specular or Lambertian)
                self.direction = intersection_object.reflectivity.reflected_direction(self, normal)
            else:
                # Specular reflection
                self.direction = reflect_vector(normal, self.direction)

                # Currently, polarisation code only runs with Fresnel reflection.
                if self.polarisation is not None:

                    ang = angle(old_direction, self.direction)
                    if cmp_floats(ang, np.pi):
                        # Anti-parallel
                        self.polarisation = self.polarisation
                    else:
                        # Apply the rotation transformation to the photon polarisation
                        # which aligns the before and after directions
                        R = rotation_matrix_from_vector_alignment(old_direction, self.direction)
                        self.polarisation = transform_direction(self.polarisation, R)

                    assert cmp_floats(angle(self.direction, self.polarisation),
                                      np.pi / 2), "Exit Pt. #1:Angle between photon direction and polarisation" \
                                                  "must be 90 degrees: theta=%s" %\
                                                  str(np.degrees(angle(self.direction, self.polarisation)))

            self.propagate = False
            self.exit_device = self.container

            # invert polarisation if n1 < n2
            if self.container.material.refractive_index < next_containing_object.material.refractive_index:

                if self.polarisation is not None:

                    if cmp_floats(ang, np.pi):
                        # Anti-parallel
                        self.polarisation *= -1.
                    else:
                        # Apply the rotation transformation to the photon polarisation
                        # which aligns the before and after directions
                        R = rotation_matrix_from_vector_alignment(old_direction, self.direction)
                        self.polarisation = transform_direction(self.polarisation, R)

                    assert cmp_floats(angle(self.direction, self.polarisation),
                                      np.pi / 2), "Exit Pt. #2: Angle between photon direction and polarisation" \
                                                  "must be 90 degrees: theta=%s"\
                                                  % str(angle(self.direction, self.polarisation))

            if self.exit_device == self.scene.bounds or self.exit_device is None:
                self.exit_device = intersection_object
            assert self.exit_device != self.scene.bounds, "The object the ray hit before hitting the bounds" \
                                                          "is the bounds. This can't be right."
            return self

        else:
            # photon is refracted through interface
            # TODO WISH: count photons leaving channels without being absorbed

            # Hackish way to account for LSC edge reflectors (0.95 hardcoded for now)
            # todo: use a v SC outer surface, face: ",edge
            #     return self

            self.propagate = True
            before = copy(self.direction)
            ang = angle(before, self.direction)

            if initialised_internally:
                # Is initialised internally
                self.direction = fresnel_refraction(normal, self.direction, self.container.material.refractive_index,
                                                    next_containing_object.material.refractive_index)
                if self.polarisation is not None:
                    if cmp_floats(ang, np.pi):
                        # Anti-parallel
                        self.polarisation = self.polarisation
                    else:
                        # Apply the rotation transformation to the photon polarisation
                        # which aligns the before and after directions
                        R = rotation_matrix_from_vector_alignment(before, self.direction)
                        self.polarisation = transform_direction(self.polarisation, R)
                    assert cmp_floats(angle(self.direction, self.polarisation),
                                      np.pi / 2), "Exit Pt. #3: Angle between photon direction and polarisation" \
                                                  "must be 90 degrees: theta=%s"\
                                                  % str(angle(self.direction, self.polarisation))

                self.exit_device = self.container
                self.previous_container = self.container
                self.container = next_containing_object

                return self

            else:
                # Initialised externally
                self.direction = fresnel_refraction(normal, self.direction, self.container.material.refractive_index,
                                                    intersection_object.material.refractive_index)

                if self.polarisation is not None:

                    if cmp_floats(ang, np.pi):
                        # Anti-parallel
                        self.polarisation = self.polarisation
                    else:
                        # Apply the rotation transformation to the photon polarisation
                        # which aligns the before and after directions
                        R = rotation_matrix_from_vector_alignment(before, self.direction)
                        self.polarisation = transform_direction(self.polarisation, R)
                        # Apply the rotation transformation to the photon polarisation
                        # which aligns the before and after directions
                    assert cmp_floats(angle(self.direction, self.polarisation),
                                      np.pi / 2), "Exit Pt. #4: Angle between photon direction and polarisation" \
                                                  "must be 90 degrees: theta=%s"\
                                                  % str(angle(self.direction, self.polarisation))

            # DJF 13.5.2010: This was crashing the statistical collection because it meant that an incident ray,
            # hitting and transmitted, then lost would have bounds as the exit_device.
            # self.exit_device = self.container
            self.exit_device = intersection_object
            self.previous_container = self.container
            self.container = intersection_object
            return self


class Tracer(object):
    """
    An object that will fire multiple photons through the scene.
    """
    def __init__(self, scene=None, source=None, throws=1, steps=50, seed=None, use_visualiser=True,
                 background=(0.957, 0.957, 1), ambient=0.5, show_axis=True,
                 show_counter=False, db_name=None, db_split=None, preserve_db_tables=False):
        # Tracer options
        super(Tracer, self).__init__()
        self.scene = scene
        self.source = source
        self.throws = throws
        self.steps = steps
        self.total_steps = 0
        self.killed = 0

        # From Scene, link db with analytics and get uuid
        self.uuid = self.scene.uuid

        self.show_counter = show_counter

        # Visualiser options
        self.show_lines = True
        self.show_exit = True
        self.show_path = True
        self.show_start = False
        self.show_normals = False

        self.seed = seed
        np.random.seed(self.seed)

        # DB SETTINGS
        self.database = pvtrace.PhotonDatabase(db_name)
        # DB splitting (performance tweak)
        # After 20k photons performance decrease is greater than 20% (compared vs. first photon simulated)
        self.split_num = self.database.split_size
        if db_split is None:
            if throws < self.split_num:
                self.db_split = False
            else:
                self.db_split = True
        else:
            self.db_split = bool(db_split)
        self.dumped = []  # Keeps a list with filenames of dumped dbs (if db_split is True and throws>split_num
        self.db_save_all_tables = preserve_db_tables

        # Object-specific settings for visualiser
        if not use_visualiser:
            pvtrace.Visualiser.VISUALISER_ON = False
        else:
            pvtrace.Visualiser.VISUALISER_ON = True
            self.visualiser = pvtrace.Visualiser(background=background, ambient=ambient, show_axis=show_axis)

            for obj in scene.objects:
                if obj != scene.bounds:
                    if not isinstance(obj.shape, CSGadd) and not isinstance(obj.shape, CSGint)\
                            and not isinstance(obj.shape, CSGsub):

                        # RayBin
                        if isinstance(obj, RayBin):
                            material = visual.materials.wood
                            colour = visual.color.blue
                            opacity = 1.
                        # Channel
                        elif isinstance(obj, Channel):
                            material = visual.materials.plastic
                            if obj.name.endswith('tubing'):
                                colour = visual.color.white
                                opacity = 0.6
                            else:
                                colour = visual.color.blue
                                opacity = 1
                        # LSC
                        elif isinstance(obj, LSC):
                            material = visual.materials.plastic
                            # FIXME LSC color set to red!
                            colour = visual.color.green
                            opacity = 0.4
                        # PlanarReflector
                        elif isinstance(obj, PlanarReflector):
                            colour = visual.color.white
                            opacity = 1.
                            material = visual.materials.plastic
                        # Coating
                        elif isinstance(obj, Coating):
                            colour = visual.color.white
                            opacity = 0.5
                            material = visual.materials.plastic

                            if hasattr(obj.reflectivity, 'lambertian'):
                                if obj.reflectivity.lambertian is True:
                                    # The material is a diffuse reflector
                                    colour = visual.color.white
                                    opacity = 1.
                                    material = visual.materials.plastic
                        # Obj whose material is SimpleMaterial
                        elif isinstance(obj.material, SimpleMaterial):
                            # import pdb; pdb.set_trace()
                            wavelength = obj.material.bandgap
                            colour = norm(wav2RGB(wavelength))
                            opacity = 0.5
                            material = visual.materials.plastic
                        else:
                            # This excludes CompositeMaterial, even if the material with highest abs. could be used.
                            if not hasattr(obj.material, 'all_absorption_coefficients'):
                                try:
                                    max_index = obj.material.emission_data.y.argmax()
                                    wavelength = obj.material.emission_data.x[max_index]
                                    colour = norm(wav2RGB(wavelength))
                                except:
                                    colour = (0.2, 0.2, 0.2)

                                opacity = 0.5
                                material = visual.materials.plastic
                            else:
                                colour = (0.2, 0.2, 0.2)
                                opacity = 0.5
                                material = visual.materials.plastic

                            if colour[0] == np.nan or colour[1] == np.nan or colour[2] == np.nan:
                                colour = (0.2, 0.2, 0.2)

                        self.visualiser.addObject(obj.shape, colour=colour, opacity=opacity, material=material)

    def start(self):
        global a, b
        logged = 0
        db_num = 0

        # Main photon loop, throws photons to the scene
        for throw in range(0, self.throws):
            # Delete last ray from visualiser
            # fixme: if channels are cylindrical in shape they will be removed from the view if this is active!
            # if pvtrace.Visualiser.VISUALISER_ON:
            #     for obj in self.visualiser.display.objects:
            #         if obj.__class__ is visual.cylinder and obj.radius < 0.001:
            #             obj.visible = False

            # SHOW COUNTER (every 10 photons)
            if throw % 10 == 0 and self.show_counter:
                sys.stdout.write('\r Photon number: ' + str(throw))
                sys.stdout.flush()

            # Create random photon from lightsource and set relative variables
            self.scene.log.debug("Emitting photon number: " + str(throw))
            photon = self.source.photon()
            photon.scene = self.scene
            photon.material = self.source

            # Sets bits for visualiser and, if show_start, shows the photon origin (with a small sphere)
            if pvtrace.Visualiser.VISUALISER_ON:
                photon.visualiser = self.visualiser
                a = list(photon.position)
                if self.show_start:
                    self.visualiser.addSmallSphere(a)

            # Photon tracing loop (up to self.steps) max iterations
            step = 0
            while photon.active and step < self.steps:
                # Save to DB the previous step (either termination or simple step)
                if photon.exit_device is not None:
                    # Adds info about exit surface, if possible
                    if photon.exit_device.shape.on_surface(photon.position):
                        # Is the ray heading towards or out of a surface?
                        normal = photon.exit_device.shape.surface_normal(photon.ray, acute=False)
                        rads = angle(normal, photon.ray.direction)
                        if rads < np.pi / 2:
                            bound = "Out"
                        else:
                            bound = "In"
                        # Saves photon to db
                        self.database.log(photon, surface_normal=photon.exit_device.shape.surface_normal(photon),
                                          surface_id=photon.exit_device.shape.surface_identifier(photon.position),
                                          ray_direction_bound=bound, emitter_material=photon.emitter_material,
                                          absorber_material=photon.absorber_material)
                    else:
                        self.database.log(photon)
                else:
                    self.database.log(photon)

                wavelength = photon.wavelength
                photon = photon.trace()

                self.scene.log.debug('Photon ' + str(throw) + ' step ' + str(step) + '...')
                if step == 0:
                    # The ray has hit the first object. 
                    # Cache this for later use. If the ray is not killed then log data.
                    entering_photon = copy(photon)

                # Visualizer bits
                if pvtrace.Visualiser.VISUALISER_ON:
                    b = list(photon.position)
                    # if self.show_lines and photon.active and step > 2:
                    if self.show_lines and photon.active:
                        self.visualiser.addLine(a, b, colour=wav2RGB(photon.wavelength))
                    
                    # if self.show_path and photon.active and step > 0:
                    if self.show_path and photon.active:
                        self.visualiser.addSmallSphere(b)
                
                # Reached Bound()
                if not photon.active and photon.container == self.scene.bounds:
                    if pvtrace.Visualiser.VISUALISER_ON:
                        if self.show_exit:
                            photon.visual_obj.append(self.visualiser.addSmallSphere(a, colour=[.33, .33, .33]))
                            photon.visual_obj.append(self.visualiser.addLine(a, a + 0.01 * photon.direction,
                                                     colour=wav2RGB(wavelength)))
                    # Record photon that has made it to the bounds
                    if step == 0:
                        self.scene.log.warn("   * Photon hit scene bounds without previous intersections "
                                            "(maybe reconsider light source position?) *")
                        print("Photon "+str(throw)+" reached BOUNDS without any intersection with scene objects!"
                                                   "[POSITION: "+str(photon.position)+","
                                                   "DIRECTION: "+str(photon.direction)+"]")
                    else:
                        self.scene.log.debug("   * Photon reached Bounds! (died)")
                        photon.exit_device.log(photon)
                        # This is not really needed and pollutes statistics
                        # self.database.log(photon)

                    # entering_photon.exit_device.log(entering_photon)
                    # assert logged == throw, "Logged (%s) and throw (%s) not equal" % (str(logged), str(throw))
                    logged += 1

                elif not photon.active:
                    photon.exit_device = photon.container
                    photon.container.log(photon)
                    self.database.log(photon)
                    if entering_photon.container == photon.scene.bounds:
                        self.scene.log.debug("   * Photon hit scene bounds without previous intersections *")
                    else:
                        # try:
                        entering_photon.container.log(entering_photon)
                        # self.database.log(photon)
                        # except:
                        #    entering_photon.container.log_in_volume(entering_photon)
                        # assert logged == throw, "Logged (%s) and thorw (%s) not equal" % (str(logged), str(throw))
                    logged += 1

                if pvtrace.Visualiser.VISUALISER_ON:
                    visual.rate(100000)  # Needed since VPyhton6
                    a = b

                step += 1
                self.total_steps += 1
                if step >= self.steps: # We need to kill the photon because it is bouncing around in a locked path
                    self.killed += 1
                    photon.killed = True
                    self.database.log(photon)
                    self.scene.log.debug("   * Reached Max Steps *")

            # DB SPLIT
            if self.db_split and throw % self.split_num == 0 and throw > 0:
                # Incremental number
                db_num = int(throw / self.split_num)
                # Commit all queries
                self.database.connection.commit()
                # Dump file location
                db_file_dump = os.path.join(self.scene.working_dir, "~pvtrace_tmp" + str(db_num) + ".sql")
                # Dump DB
                self.database.dump_to_file(location=db_file_dump)
                # Add DB dumped file to dumped list for later recovery
                self.dumped.append(db_file_dump)
                # Empty current DB
                self.database.empty()

        # Commit DB
        self.database.connection.commit()
        # If DB split is active, split the remaining photons and then merge everything
        if self.db_split:
            db_num += 1
            db_file_dump = os.path.join(self.scene.working_dir, "~pvtrace_tmp" + str(db_num) + ".sql")
            self.database.dump_to_file(location=db_file_dump)
            self.dumped.append(db_file_dump)

            # MERGE DB before statistics
            # this will be done in memory only (RAM is cheap nowadays)
            self.database = pvtrace.PhotonDatabase(dbfile=None)
            # Check whether to save all the DB tables of just photon and state (faster and smaller but with data loss)
            if self.db_save_all_tables:
                tables_to_save = None
            else:
                tables_to_save = ("photon", "state")
            
            for db_file in self.dumped:
                self.database.add_db_file(filename=db_file, tables=tables_to_save)
                # Removes dumps
                os.remove(db_file)

        # Save DB to Scene as db.sqlite file (merged DB if split is active, the only active DB otherwise)
        self.scene.stats.add_db(self.database)
        db_final_location = os.path.join(self.scene.working_dir, 'db.sqlite')
        self.database.dump_to_file(db_final_location)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)

