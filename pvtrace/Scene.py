from __future__ import division, print_function

import os
import time

import shortuuid

import pvtrace.Analysis
import pvtrace.PhotonDatabase
import pvtrace.Scene
from pvtrace.Devices import *

try:
    import visual
    from Visualise import Visualiser
except Exception:
    pass


class Scene(object):
    """
    A collection of objects. All intersection points can be found or a ray can be traced through.
    """

    def __init__(self, uuid=None, force=False, level=logging.INFO):
        super(Scene, self).__init__()
        self.bounds = Bounds()  # Create boundaries to world and apply to scene
        self.objects = [self.bounds]
        self.uuid = ''
        self.working_dir = self.get_new_working_dir(uuid=uuid, use_existing=force)
        print("Working directory: ", self.working_dir)
        self.log = self.start_logging(level)
        self.stats = pvtrace.Analysis(uuid=self.uuid)

    def start_logging(self, level=None):
        LOG_FILENAME = os.path.join(self.working_dir, 'output.log')
        # Create file if needed and without truncating (appending useful for post-mortem DB analysis)
        open(LOG_FILENAME, 'a').close()

        # LOGGING SETTINGS
        # Ensure that existing handlers are removed so that the new location for log file can be enforced
        log = logging.getLogger()
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        # Start logging on output.log in Scene directory
        if level is not None:
            logging.basicConfig(filename=LOG_FILENAME, filemode='a', level=level)
        else:
            logging.basicConfig(filename=LOG_FILENAME, filemode='a', level=logging.INFO)

        logger = logging.getLogger('pvtrace.scene')
        logger.debug('*** NEW SIMULATION ***')
        logger.info('UUID: ' + self.uuid)
        logger.debug('Date/Time ' + time.strftime("%c"))
        return logger

    def get_new_working_dir(self, uuid=None, use_existing=None):
        # Check if uuid is None or empty
        if uuid is None or not uuid:
            try_uuid = shortuuid.uuid()
        else:
            try_uuid = uuid

        working_dir = os.path.join('D:/','LSC_PM_simulation_results', 'test_tilt_LSC', try_uuid)

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
                             "my_device.name='my unique name'." % object_to_add.name)
        self.objects.append(object_to_add)

    def add_objects(self, objects_to_add):
        """
        Adds a list of objects to the scene.

        :param objects_to_add: list with the objects to be added.
        """
        if len(objects_to_add) == 0:
            return
        if len(objects_to_add) == 1:
            self.add_object(objects_to_add[0])
            return True

        for obj in objects_to_add:
            self.add_object(obj)

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

    def sort(self, points, objects, ray, container=None, remove_ray_intersection=True):
        """
        Returns points and objects sorted by separation from the ray position.

        :param points: a list of intersection points as returned by scene.intersection(ray)
        :param objects: a list of objects as returned by scene.intersection(ray)
        :param ray: a ray with global coordinate frame
        :param container: the container
        :param remove_ray_intersection: if the ray is on an intersection points remove this point from both lists
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
            self.log.debug("Obj: \t" + str(objects))
            self.log.debug("Points: \t" + str(points))

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
