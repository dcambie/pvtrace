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
from copy import copy

import shortuuid

import pvtrace.Analysis
import pvtrace.PhotonDatabase
import pvtrace.external.pov as pov
from pvtrace.Devices import *

try:
    import visual
    from Visualise import Visualiser
except Exception:
    pass

# import multiprocessing
# cpu_count = multiprocessing.cpu_count()
POVRAY_BINARY = ("pvengine.exe" if os.name == 'nt' else "pvtrace")


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

    def __init__(self, wavelength=555, position=None, direction=None, active=True, show_log=True):
        """
        Initialize the photon.

        All arguments are optional because a photon is created with default values.
        :param wavelength: the photon wavelength in nanometers (float).
        :param position: the photon position in cartesian coordinates is an array-like quantity in units of metres
        :param direction: the photon Cartesian direction vector (3 elements), a normalised vector is array-like
        :param active: boolean indicating if the ray has or has not been lost (e.g. absorbed in a material)
        :param show_log: print verbose output on photon fate during tracing

        >>> a = Photon()
        >>> a.wavelength
        555
        >>> a.position
        array([ 0.,  0.,  0.])
        >>> a.direction
        array([ 0.,  0.,  1.])
        >>> a.active
        True
        >>> a.show_log
        True
        >>> a.wavelength = 600
        >>> b = a
        >>> b.wavelength
        600
        >>> a.ray
        <pvtrace.Geometry.Ray object at ...
        >>> print(a)
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
        self.show_log = show_log
        self.reabs = 0
        self.id = 0
        self.source = None
        self.absorption_counter = 0
        self.intersection_counter = 0
        self.reaction = False
        self.previous_container = None

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
        photon_copy.show_log = self.show_log
        photon_copy.reabs = self.reabs
        photon_copy.id = self.id
        photon_copy.source = self.source
        photon_copy.absorber_material = self.absorber_material
        photon_copy.emitter_material = self.emitter_material
        photon_copy.on_surface_object = self.on_surface_object
        photon_copy.reaction = self.reaction
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

    def isReaction(self):
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
                                                                    container=self.container, show_log=self.show_log)

        # find current intersection point and object -- should be zero if the list is sorted!
        intersection = closest_point(self.position, intersection_points)
        for i in range(0, len(intersection_points)):
            if list(intersection_points[i]) == list(intersection):
                index = i
                break

        # import pdb; pdb.set_trace()
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
            elif not isinstance(intersection_object, Coating) and isinstance(next_containing_object, Coating):
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


def povObj(obj, colour=None):
    # print type(obj)
    try:
        T = obj.transform
        white = pov.Texture(pov.Pigment(color="White", transmit=0.5)) if colour is None else colour
        M = "< %s >" % (", ".join(str(T[:3].transpose().flatten())[1:-1].replace("\n", "").split()))
    except:
        pass

    if type(obj) == Cylinder:
        return pov.Cylinder((0, 0, 0), (0, 0, obj.length), obj.radius, white, matrix=M)
    if type(obj) == Box:
        return pov.Box(tuple(obj.origin), tuple(obj.extent), white, matrix=M)
    if type(obj) == Coating:
        return povObj(obj.shape)
    if type(obj) == LSC:
        # maxindex = obj.material.emission.y.argmax()
        # wavelength = obj.material.emission.x[maxindex]
        # colour = wav2RGB(633)
        # print color # value is [255, 47, 0]
        # Red for LSC is now hardcoded :(
        colour = [236, 13, 36]
        colour = pov.Pigment(color=(colour[0] / 255, colour[1] / 255, colour[2] / 255, 0.85))  # 0.85 is transparency
        return povObj(obj.shape, colour=colour)
    if type(obj) == Plane:
        return pov.Plane((0, 0, 1), 0, white, matrix=M)
    if type(obj) == FinitePlane:
        return pov.Box((0, 0, 0), (obj.length, obj.width, 0), white, matrix=M)
    if type(obj) == CSGsub:
        return pov.Difference(povObj(obj.SUBplus), povObj(obj.SUBminus))
    if type(obj) == CSGadd:
        return pov.Union(povObj(obj.ADDone), povObj(obj.ADDtwo))
    if type(obj) == CSGint:
        return pov.Intersection(povObj(obj.INTone), povObj(obj.INTtwo))
    if type(obj) == RayBin:
        colour = pov.Pigment(color=(0, 0, 0.5, 1))  # BLUE (rgb/255)
        return povObj(obj.shape, colour=colour)
    if type(obj) == Channel:
        colour = pov.Pigment(color=(0, 0, 0.5, 1))  # BLUE (rgb/255)
        return povObj(obj.shape, colour=colour)
    print("Uncaught object type! TYPE:", type(obj), " VALUE: ", obj)


class Scene(object):
    """
    A collection of objects. All intersection points can be found or a ray can be traced through.
    """

    def pov_render(self, camera_position=(0, 0, 0.1), camera_target=(0, 0, 0), height=2400, width=3200):
        """
        Pov thing

        :param camera_position: position of the camera
        :param camera_target:  aim for camera
        :param height: output render image height size in pixels
        :param width: output render image width size in pixels
        :return: Creates the render image but returns nothing

        doctest: +ELLIPSIS
        >>> S = Scene('overwrite_me')
        Working directory: ...
        >>> L, W, D = 1, 1, 1
        >>> box = Box(origin=(-L/2., -W/2.,-D/2.), extent=(L/2, W/2, D/2))
        >>> box.name = 'box'
        >>> myCylinder = Cylinder(radius=1)
        >>> myCylinder.name = 'cyl'
        >>> myCylinder.append_transform(tf.translation_matrix((0,-1,0)))
        >>> box.append_transform(tf.rotation_matrix(-np.pi/3,(0,1,0), point=(0,0,0)))
        >>> # S.add_object(CSGsub(myCylinder, box))
        >>> myPlane = FinitePlane()
        >>> myPlane.name = 'Plane'
        >>> myPlane.append_transform(tf.translation_matrix((0,0,9.9)))
        >>> S.add_object(myPlane)
        >>> S.add_object(box)
        >>> S.add_object(myCylinder)
        >>> S.pov_render(width=800, height=600)
        """

        #        """
        f = pov.File("demo.pov", "colors.inc", "stones.inc")

        cam = pov.Camera(location=camera_position, sky=(1, 0, 1), look_at=camera_target)
        light = pov.LightSource(camera_position, color="White")

        povObjs = [cam, light]
        for obj in self.objects[1:]:
            povObjs.append(povObj(obj))

        # print tuple(povObjs)
        f.write(*tuple(povObjs))
        f.close()

        # A for anti-aliasing, q is quality (1-11)
        subprocess.call(POVRAY_BINARY + " +A +Q10 +H" + str(height) + " +W" + str(width) + " demo.pov", shell=True)
        file_opener("demo.png")

    #        """

    def __init__(self, uuid=None, force=False):
        super(Scene, self).__init__()
        self.bounds = Bounds()  # Create boundaries to world and apply to scene
        self.objects = [self.bounds]
        self.uuid = None
        self.working_dir = self.get_new_working_dir(uuid=uuid, use_existing=force)
        print("Working directory: ", self.working_dir)
        self.log = self.start_logging()
        self.stats = pvtrace.Analysis.Analysis(uuid=self.uuid)

    def start_logging(self):
        LOG_FILENAME = os.path.join(self.working_dir, 'output.log')

        # Create file if needed and without truncating (appending useful for post-mortem DB analysis)
        open(LOG_FILENAME, 'a').close()
        # logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
        logger = logging.getLogger('pvtrace.trace')
        logger.debug('*** NEW SIMULATION ***')
        logger.info('UUID: ' + self.uuid)
        logger.debug('Date/Time ' + time.strftime("%c"))
        return logger

    def get_new_working_dir(self, uuid=None, use_existing=None):
        if uuid is None:
            try_uuid = shortuuid.uuid()
        else:
            try_uuid = uuid

        working_dir = os.path.join(os.path.expanduser('~'), 'pvtrace_data', try_uuid)

        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
            self.uuid = try_uuid
            return working_dir
        elif try_uuid == 'overwrite_me':
            self.uuid = try_uuid
            return working_dir
        elif use_existing:
            self.uuid = try_uuid
            return working_dir
        else:
            raise NameError("Working dir "+str(working_dir)+" already existing!")

    def add_object(self, object_to_add):
        """
        Adds a new object to the scene.

        :param object_to_add: object to be added. Needs a unique name!
        """
        if len(object_to_add.name) == 0:
            raise ValueError('The name of the object being added to the scene is blank, please give your scene'
                             'element (i.e. Devices) a name by doing: my_device.name="my unique name".')

        names = []
        for obj in self.objects:
            names.append(obj.name)
        names = set(names)
        count = len(names)
        names.add(object_to_add.name)
        if count == len(names):
            # The name of the new object is a duplicate
            raise ValueError("The name of the object being added, '%s' is not unique. All seem objects (i.e. Devices) "
                             "must have unique name. You can change the name easily by doing:"
                             "my_device.name='my unique name'.", object_to_add.name)
        self.objects.append(object_to_add)

    def intersection(self, ray):
        """
        Returns the intersection points and associated objects of a ray in no particular order.

        :param ray: Ray to be evaluated for intersections
        """
        points = []
        intersection_objects = []
        for obj in self.objects:
            intersection = obj.shape.intersection(ray)
            if intersection is not None:
                for pt in intersection:
                    points.append(pt)
                    intersection_objects.append(obj)
                    # else:
                    # print obj.name

        if len(points) == 0:
            return None, None
        return points, intersection_objects

    def sort(self, points, objects, ray, container=None, remove_ray_intersection=True, show_log=False):
        """
        Returns points and objects sorted by separation from the ray position.

        :param points: a list of intersection points as returned by scene.intersection(ray)
        :param objects: a list of objects as returned by scene.intersection(ray)
        :param ray: a ray with global coordinate frame
        :param container: the container
        :param remove_ray_intersection: if the ray is on an intersection points remove this point from both lists
        :param show_log: if true objects and points are printed to stout (*very* verbose, set a low throw!)
        """

        # Filter arrays for intersection points that are ahead of the ray's direction
        # also if the ray is on an intersection already remove it (optional)
        for i in range(0, len(points)):

            if remove_ray_intersection:
                try:
                    if ray.ray.behind(points[i]) or cmp_points(ray.position, points[i]):
                        points[i] = None
                        objects[i] = None
                except:
                    # import pdb; pdb.set_trace()
                    ray.ray.behind(points[i])
                    cmp_points(ray.position, points[i])
                    exit(1)
            else:
                if ray.ray.behind(points[i]):
                    points[i] = None
                    objects[i] = None

        objects = [item for item in objects if item]
        points_copy = list(points)
        points = []

        for i in range(0, len(points_copy)):
            if points_copy[i] is not None:
                points.append(points_copy[i])

        assert len(points) > 0, "No intersection points can be found with the scene."

        # sort the intersection points arrays by separation from the ray's position
        separations = []
        for point in points:
            separations.append(separation(ray.position, point))
        sorted_indices = np.argsort(separations)
        separations.sort()

        # Sort according to sort_indices array
        points_copy = list(points)
        objects_copy = list(objects)
        for i in range(0, len(points)):
            points[i] = points_copy[sorted_indices[i]]
            objects[i] = objects_copy[sorted_indices[i]]
        del points_copy
        del objects_copy

        if self.log.isEnabledFor(logging.DEBUG):
            self.log("Obj: \t" + str(objects))
            self.log("Points: \t" + str(points))

        objects, points, separations = Scene.order_duplicates(objects, points, separations)

        # Now perform container check on ordered duplicates
        if container is not None:
            if objects[0] != container and len(objects) > 1:
                # The first object in the array must be the container so there is an order problem
                # assumes container object is an index 1!
                obj = objects[1]
                objects[1] = objects[0]
                objects[0] = obj

                obj = points[1]
                points[1] = points[0]
                points[0] = obj

                obj = points[1]
                separations[1] = separations[0]
                separations[0] = obj

                trim_objs, trim_pts, trim_sep = Scene.order_duplicates(objects[1::], points[1::], separations[1::])
                objects[1::] = trim_objs
                points[1::] = trim_pts
                separations[1::] = trim_sep

        return points, objects

    def order_duplicates(objects, points, separations):
        """
        Subroutine which might be called recursively by the sort function when the first element
        of the objects array is not the container objects after sorting.

        :param objects: a list of objects as returned by scene.intersection(ray)
        :param points: a list of intersection points as returned by scene.intersection(ray)
        :param separations:
        """

        # If two intersections occur at the same points then the sort order won't always be correct.
        # We need to sort by noticing the order of the points that could be sorted.
        # (e.g.) a thin-film from air could give [a {b a} b], this pattern, we know the first point is correct.
        # (e.g.) a thin-film from thin-film could give [{b a} b c], this pattern,  we know the middle is point correct.
        # (e.g.) another possible example when using CGS objects [a b {c b} d].
        # (e.g.) [a {b a} b c] --> [a a b b c]
        # (e.g.) need to make the sort algorithm always return [a a b b] or [a b b c].
        # Find indices of same-separation points

        if (len(objects)) > 2:
            common = []
            for i in range(0, len(separations) - 1):
                if cmp_floats(separations[i], separations[i + 1]):
                    common.append(i)

            # If the order is incorrect then we swap two elements (as described above)
            for index in common:

                if not (objects[index + 1] == objects[index + 2]):
                    # We have either [{b a} b c], or [{a b} b c]
                    obj = objects[index + 1]
                    objects[index + 1] = objects[index]
                    objects[index] = obj

                    obj = points[index + 1]
                    points[index + 1] = points[index]
                    points[index] = obj

                    obj = separations[index + 1]
                    separations[index + 1] = separations[index]
                    separations[index] = obj

        return objects, points, separations

    order_duplicates = staticmethod(order_duplicates)

    def container(self, photon):
        """
        Returns the inner most object that contains the photon.

        :param photon: the contained photon
        """

        # Ask each object if it contains the photon.
        # If multiple object return true we filter by separation to find the inner container.
        containers = []
        for obj in self.objects:
            if obj.shape.contains(photon.position):
                containers.append(obj)

        if len(containers) == 0:
            raise ValueError("The photon is not located inside the scene bounding box.")
        elif len(containers) == 1:
            return containers[0]
        else:
            # We cast the ray forward and make intersections with the possible containers
            # The inner container is individuated by the closest intersection point
            separations = []
            for obj in containers:
                intersection_point = obj.shape.intersection(photon)
                assert len(intersection_point) == 1, "A primitive containing object can only have one" \
                                                     "intersection point with a line when the origin of the test ray" \
                                                     "is contained by the object."
                separations.append(separation(photon.position, intersection_point[0]))
            min_index = np.array(separations).argmin()
            return containers[min_index]


class Tracer(object):
    """
    An object that will fire multiple photons through the scene.
    """
    def __init__(self, scene=None, source=None, throws=1, steps=50, seed=None, use_visualiser=True, show_log=False,
                 background=(0.957, 0.957, 1), ambient=0.5, show_axis=True,
                 show_counter=False, db_split=None):
        super(Tracer, self).__init__()
        self.scene = scene
        self.source = source
        self.throws = throws
        self.steps = steps
        self.total_steps = 0
        self.seed = seed
        self.killed = 0
        self.database = pvtrace.PhotonDatabase.PhotonDatabase(None)
        self.show_log = show_log
        self.show_counter = show_counter
        # From Scene, link db with analytics and get uuid
        self.uuid = self.scene.uuid

        # DB splitting (performance tweak)
        self.split_num = self.database.split_size

        if db_split is None:
            if throws < self.split_num:
                self.db_split = False
            else:
                self.db_split = True
        else:
            self.db_split = bool(db_split)

        self.dumped = []  # Keeps a list with filenames of dumped db (if db_split is True and throws>split_num
        # After 20k photons performance decrease is greater than 20% (compared vs. first photon simulated)

        np.random.seed(self.seed)
        if not use_visualiser:
            pvtrace.Visualiser.VISUALISER_ON = False
        else:
            pvtrace.Visualiser.VISUALISER_ON = True
            self.visualiser = pvtrace.Visualiser(background=background, ambient=ambient, show_axis=show_axis)

            for obj in scene.objects:
                if obj != scene.bounds:
                    if not isinstance(obj.shape, CSGadd) and not isinstance(obj.shape, CSGint)\
                            and not isinstance(obj.shape, CSGsub):

                        # import pdb; pdb.set_trace()
                        if isinstance(obj, RayBin):
                            # checkerboard = ( (0,0.01,0,0.01), (0.01,0,0.01,0), (0,0.01,0,1), (0.01,0,0.01,0) )
                            # checkerboard = ( (0,1,0,1), (1,0,1,0), (0,1,0,1), (1,0,1,0) )
                            # material = visual.materials.texture(data=checkerboard, mapping="rectangular",
                            #                                     interpolate=False)
                            material = visual.materials.wood
                            colour = visual.color.blue
                            opacity = 1.

                        elif isinstance(obj, Channel):
                            material = visual.materials.wood
                            colour = visual.color.blue
                            opacity = 1.
                        # Dario's edit: LSC color set to red/
                        # this breaks multiple lSC colours in the same scene. sorry :)
                        elif isinstance(obj, LSC):
                            material = visual.materials.plastic
                            colour = visual.color.red
                            opacity = 0.2

                        elif isinstance(obj, PlanarReflector):
                            colour = visual.color.white
                            opacity = 1.
                            material = visual.materials.plastic

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
                                # It is possible to processes the most likely colour of a spectrum in a better way than this
                                colour = (0.2, 0.2, 0.2)
                                opacity = 0.5
                                material = visual.materials.plastic

                            if colour[0] == np.nan or colour[1] == np.nan or colour[2] == np.nan:
                                colour = (0.2, 0.2, 0.2)

                        self.visualiser.addObject(obj.shape, colour=colour, opacity=opacity, material=material)

        self.show_lines = True  # False
        self.show_exit = True
        self.show_path = True  # False
        self.show_start = False  # Was True
        self.show_normals = False

    def start(self):
        global a, b
        logged = 0
        db_num = 0
        for throw in range(0, self.throws):
            # import pdb; pdb.set_trace()
            # Delete last ray from visualiser
            # fixme: if channels are cylindrical in shape they will be removed from the view if this is active!
            # if pvtrace.Visualiser.VISUALISER_ON:
            #     for obj in self.visualiser.display.objects:
            #         if obj.__class__ is visual.cylinder and obj.radius < 0.001:
            #             obj.visible = False
            # DB speed statistics
            # if throw == 0:
            #     then = time.clock()
            # elif throw % 100 == 0:
            #     now = time.clock()
            #     zeit = now - then
            #     sys.stdout.write('\r' + str(throw) + " " + str(zeit).rjust(6, ' '))
            #     print
            #     then = now

            self.scene.log.debug("Photon number: "+str(throw))
            if self.show_counter:
                sys.stdout.write('\r Photon number: ' + str(throw))
                sys.stdout.flush()

            # Create random photon from lightsource and set relative variables
            photon = self.source.photon()
            photon.scene = self.scene
            photon.material = self.source
            photon.show_log = self.show_log

            if pvtrace.Visualiser.VISUALISER_ON:
                photon.visualiser = self.visualiser
                a = list(photon.position)
                if self.show_start:
                    self.visualiser.addSmallSphere(a)

            step = 0
            while photon.active and step < self.steps:

                if photon.exit_device is not None:

                    # The exit
                    if photon.exit_device.shape.on_surface(photon.position):

                        # Is the ray heading towards or out of a surface?
                        normal = photon.exit_device.shape.surface_normal(photon.ray, acute=False)
                        rads = angle(normal, photon.ray.direction)
                        # print(photon.exit_device.shape.surface_identifier(photon.position),
                        #       'normal', normal, 'ray dir', photon.direction, 'angle' , np.degrees(rads))
                        if rads < np.pi / 2:
                            bound = "Out"
                            # print "OUT"
                        else:
                            bound = "In"
                            # print "IN"

                        self.database.log(photon, surface_normal=photon.exit_device.shape.surface_normal(photon),
                                          surface_id=photon.exit_device.shape.surface_identifier(photon.position),
                                          ray_direction_bound=bound, emitter_material=photon.emitter_material,
                                          absorber_material=photon.absorber_material)

                else:
                    self.database.log(photon)

                # import time;
                # time.sleep(0.1)
                # import pdb; pdb.set_trace()
                wavelength = photon.wavelength
                # photon.visualiser.addPhoton(photon)
                photon = photon.trace()

                if step == 0:
                    # The ray has hit the first object. 
                    # Cache this for later use. If the ray is not 
                    # killed then log data.
                    # import pdb; pdb.set_trace()
                    entering_photon = copy(photon)

                # print "Step number:", step
                if pvtrace.Visualiser.VISUALISER_ON:
                    b = list(photon.position)
                    # if self.show_lines and photon.active and step > 0:
                    if self.show_lines and photon.active:
                        self.visualiser.addLine(a, b, colour=wav2RGB(photon.wavelength))

                    # if self.show_path and photon.active and step > 0:
                    if self.show_path and photon.active:
                        self.visualiser.addSmallSphere(b)

                # import pdb; pdb.set_trace()
                if not photon.active and photon.container == self.scene.bounds:

                    # import pdb; pdb.set_trace()
                    if pvtrace.Visualiser.VISUALISER_ON:
                        if self.show_exit:
                            self.visualiser.addSmallSphere(a, colour=[.33, .33, .33])
                            self.visualiser.addLine(a, a + 0.01 * photon.direction, colour=wav2RGB(wavelength))

                    # Record photon that has made it to the bounds
                    if step == 0:
                        self.scene.log.debug("   * Photon hit scene bounds without previous intersections "
                                             "(maybe reconsider light source position?) *")
                    else:
                        self.scene.log.debug("   * Reached Bounds *")
                        photon.exit_device.log(photon)
                        # self.database.log(photon)

                    # entering_photon.exit_device.log(entering_photon)
                    # assert logged == throw, "Logged (%s) and thorw (%s) not equal" % (str(logged), str(throw))
                    logged += 1

                elif not photon.active:
                    # print photon.exit_device.name
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
                    # assert logged == throw, "Logged (%s) and throw (%s) are not equal" % (str(logged), str(throw))
                    logged += 1

                # Needed since VPyhton6
                if pvtrace.Visualiser.VISUALISER_ON:
                    visual.rate(100000)
                    a = b

                step += 1
                self.total_steps += 1
                if step >= self.steps:
                    # We need to kill the photon because it is bouncing around in a locked path
                    self.killed += 1
                    photon.killed = True
                    self.database.log(photon)
                    self.scene.log.debug("   * Reached Max Steps *")

            # Split DB if needed
            if self.db_split and throw % self.split_num == 0 and throw > 0:
                db_num = int(throw / self.split_num)
                self.database.connection.commit()
                # db_file_dump = os.path.join(os.path.expanduser('~'), "~pvtrace_tmp" + str(db_num) + ".sql")
                db_file_dump = os.path.join(self.scene.working_dir, "~pvtrace_tmp" + str(db_num) + ".sql")
                self.database.dump_to_file(location=db_file_dump)
                self.dumped.append(db_file_dump)
                # Empty DB
                self.database.empty()

        # Commit DB
        self.database.connection.commit()
        if self.db_split:
            db_num += 1
            db_file_dump = os.path.join(self.scene.working_dir, "~pvtrace_tmp" + str(db_num) + ".sql")
            self.database.dump_to_file(location=db_file_dump)
            self.dumped.append(db_file_dump)

            # MERGE DB before statistics
            # this will be done in memory only (RAM is cheap nowadays)
            self.database = pvtrace.PhotonDatabase.PhotonDatabase(dbfile=None)
            for db_file in self.dumped:
                self.database.add_db_file(filename=db_file, tables=("photon", "state"))
                os.remove(db_file)
                # print "merged ",db_file

        # Finalize merged DB
        self.scene.stats.add_db(self.database)
        db_final_location = os.path.join(self.scene.working_dir, 'db.sqlite')
        self.database.dump_to_file(db_final_location)

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)