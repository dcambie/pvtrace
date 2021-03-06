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
try:
    import visual
    VISUAL_INSTALLED = True
    print("Python module visual is installed...")
except:
    print("Python module visual is not installed...  all Visualiser are disabled.")
    VISUAL_INSTALLED = False

import numpy as np
import pvtrace.Geometry as Geo
import pvtrace.ConstructiveGeometry as Csg
import pvtrace.external.transformations as tf


class Visualiser (object):
    """
    Visualiser a class that converts project geometry objects into vpython objects and draws them.

    It can be used pragmatically: just add objects as they are created and the changes will update in the display.
    Note: the Scene can be controlled with awsd keys
    """
    VISUALISER_ON = True
    if not VISUAL_INSTALLED:
        VISUALISER_ON = False

    def keyInput(self, evt):
        s = evt.key

        if len(s) == 1:
            if s == 'x':
                print(self.display.center)
                print(self.display.forward)
                
            if s == 'd':
                self.display.center = (self.display.center[0]+0.005, self.display.center[1], self.display.center[2])
            if s == 's':
                self.display.center = (self.display.center[0], self.display.center[1]-0.005, self.display.center[2])
            if s == 'a':
                self.display.center = (self.display.center[0]-0.005, self.display.center[1], self.display.center[2])
            if s == 'w':
                self.display.center = (self.display.center[0], self.display.center[1]+0.005, self.display.center[2])
            if s == 'r':
                self.display.center = (self.display.center[0], self.display.center[1] + 0.0005, self.display.center[2])
            if s == '0':
                self.display.center = (0.035, 0.03, 0)
                self.display.center = (1.6, 1.611, 0)
                self.display.forward = (0, 0.75, -0.5)
            if s == 'z':
                self.display.center = (0.025, 0.025, 0.0015)
                self.display.forward = (0.5, 0, 0)
            if s == 'q':
                Visualiser.VISUALISER_ON = False
            if s == '1':
                self.display.forward = self.display.forward.rotate(angle=0.1, axis=(0, 0, 1))
            if s == '2':
                self.display.forward = self.display.forward.rotate(angle=-0.1, axis=(0, 0, 1))
            if s == '3':
                self.display.forward = self.display.forward.rotate(angle=0.1, axis=(1, 0, 0))
            if s == '4':
                self.display.forward = self.display.forward.rotate(angle=-0.1, axis=(1, 0, 0))
            if s == '5':
                self.display.forward = self.display.forward.rotate(angle=0.1, axis=(0, 1, 0))
            if s == '6':
                self.display.forward = self.display.forward.rotate(angle=-0.1, axis=(0, 1, 0))
            if s == 'p':
                print("Forward: " + str(self.display.forward))
                print("Center: " + str(self.display.center))
            if s == '[':
                print("Forward: " + str(self.display.forward))
                print("Center: " + str(self.display.center))
            if s == '[':
                print("Forward: " + str(self.display.forward))
                print("Center: " + str(self.display.center))

    def __init__(self, background=None, ambient=None, show_axis=True):
        super(Visualiser, self).__init__()
        if not Visualiser.VISUALISER_ON:
            return

        if background is None:
            background = (0.957, 0.957, 1)
        if ambient is None:
            ambient = 0.5
        self.display = visual.display(title='PVTrace', x=0, y=0, width=800, height=600, background=background,
                                      ambient=ambient)
        self.display.bind('keydown', self.keyInput)
        self.display.exit = False

        self.display.center = (0.025, 0.015, 0)
        self.display.forward = (0, 0.83205, -0.5547)
        
        show_axis = False
        if show_axis:
            visual.curve(pos=[(0, 0, 0), (.08, 0, 0)], radius=0.0005, color=visual.color.red)
            visual.curve(pos=[(0, 0, 0), (0, .07, 0)], radius=0.0005, color=visual.color.green)
            visual.curve(pos=[(0, 0, 0), (0, 0, .08)], radius=0.0005, color=visual.color.blue)
            visual.label(pos=(.09, 0, 0), text='X', background=visual.color.red, linecolor=visual.color.red)
            visual.label(pos=(0, .08, 0), text='Y', background=visual.color.green, linecolor=visual.color.green)
            visual.label(pos=(0, 0, .07), text='Z', background=visual.color.blue, linecolor=visual.color.blue)
    
    def addBox(self, box_to_add, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return
        if isinstance(box_to_add, Geo.Box):
            if colour is None:
                colour = visual.color.red
            org = Geo.transform_point(box_to_add.origin, box_to_add.transform)
            ext = Geo.transform_point(box_to_add.extent, box_to_add.transform)
            # print "Visualiser: box origin=%s, extent=%s" % (str(org), str(ext))
            box_size = np.abs(ext - org)
            
            pos = org + 0.5*box_size
            # print "Visualiser: box position=%s, box_size=%s" % (str(pos), str(box_size))
            angle, direction, point = tf.rotation_from_matrix(box_to_add.transform)

            if material is None:
                material = visual.materials.plastic

            if np.allclose(np.array(colour), np.array([0, 0, 0])):
                visual.box(pos=pos, size=box_size, material=material, opacity=opacity)
            else:
                visual.box(pos=pos, size=box_size, color=colour, materials=material, opacity=opacity)
    
    def addSphere(self, sphere_to_add, colour=None, opacity=1., material=None):
        """docstring for addSphere"""
        if not Visualiser.VISUALISER_ON:
            return

        if material is None:
            material = visual.materials.plastic
        
        if isinstance(sphere_to_add, Geo.Sphere):
            if colour is None:
                colour = visual.color.red
            if np.allclose(np.array(colour), np.array([0, 0, 0])):
                visual.sphere(pos=sphere_to_add.centre, radius=sphere_to_add.radius, opacity=opacity, material=material)
            else:
                visual.sphere(pos=sphere_to_add.centre, radius=sphere_to_add.radius, color=Geo.norm(colour),
                              opacity=opacity, material=material)
            
    def addFinitePlane(self, plane, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return

        if material is None:
            material = visual.materials.plastic

        if isinstance(plane, Geo.FinitePlane):
            if colour is None:
                colour = visual.color.blue
            # visual doesn't support planes, so we draw a very thin box
            H = .001
            pos = (plane.length/2, plane.width/2, H/2)
            pos = Geo.transform_point(pos, plane.transform)
            size = (plane.length, plane.width, H)
            axis = Geo.transform_direction((0, 0, 1), plane.transform)
            visual.box(pos=pos, size=size, color=colour, opacity=opacity, material=material)

    def addPolygon(self, polygon, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return

        if material is None:
            material = visual.materials.plastic

        if isinstance(polygon, Geo.Polygon):
            if colour is None:
                visual.convex(pos=polygon.pts, color=Geo.norm([0.1, 0.1, 0.1]), material=material)
            else:
                visual.convex(pos=polygon.pts, color=Geo.norm(colour), material=material)
    
    def addConvex(self, convex, colour=None, opacity=1., material=None):
        """docstring for addConvex"""
        if not Visualiser.VISUALISER_ON:
            return

        if material is None:
                material = visual.materials.plastic

        if isinstance(convex, Geo.Convex):
            if colour is None:
                print("Color is none")
                visual.convex(pos=convex.points, color=Geo.norm([0.1, 0.1, 0.1]), material=material)
            else:
                print("Color is", Geo.norm(colour))
                visual.convex(pos=convex.points, color=Geo.norm(colour), material=material)
                
    def addRay(self, ray, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return
        if isinstance(ray, Geo.Ray):
            if colour is None:
                colour = visual.color.white
            pos = ray.position
            axis = ray.direction * 5
            visual.cylinder(pos=pos, axis=axis, radius=0.0001, color=Geo.norm(colour),
                            opacity=opacity, material=material)
    
    def addSmallSphere(self, point, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return
        if colour is None:
            # colour = visual.color.blue
            colour = visual.color.gray(0.2)
        return visual.sphere(pos=point, radius=0.00006, color=Geo.norm(colour), opacity=opacity, materiall=material)
        # visual.curve(pos=[point], radius=0.0005, color=geo.norm(colour))

    def addLine(self, start, stop, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return
        if colour is None:
            colour = visual.color.white
        axis = np.array(stop) - np.array(start)
        return visual.cylinder(pos=start, axis=axis, radius=0.000055, color=Geo.norm(colour),
                               opacity=opacity, material=material)
    
    def addCylinder(self, cylinder, colour=None, opacity=1., material=None):
        if not Visualiser.VISUALISER_ON:
            return
        if colour is None:
            colour = visual.color.blue

        # angle, direction, point = tf.rotation_from_matrix(cylinder.transform)
        # axis = direction * cylinder.length
        position = Geo.transform_point([0, 0, 0], cylinder.transform)
        axis = Geo.transform_direction([0, 0, 1], cylinder.transform)
        # print cylinder.transform, "Cylinder:transform"
        # print position, "Cylinder:position"
        # print axis, "Cylinder:axis"
        # print colour, "Cylinder:colour"
        # print cylinder.radius, "Cylinder:radius"
        visual.cylinder(pos=position, axis=axis, color=colour, radius=cylinder.radius, opacity=opacity,
                        length=cylinder.length, material=material)

    def addCSG(self, CSGobj, res, origin, extent, colour=None, opacity=1., material=None):
        """
        Visualise a CSG structure in a space subset defined by xmin, xmax, ymin,
        and with division factor (i.e. ~ resolution) res
        """

        xmin = origin[0]
        xmax = extent[0]
        ymin = origin[1]
        ymax = extent[1]
        zmin = origin[2]
        zmax = extent[2]

        """
        Determine Voxel size from resolution
        """
        voxelextent = (res*(xmax-xmin), res*(ymax-ymin), res*(zmax-zmin))
        pex = voxelextent

        """
        Scan space
        """
        
        x = xmin
        
        print('Visualisation of ', CSGobj.reference, ' started...')
            
        while x < xmax:

            y = ymin
            z = zmin
                  
            while y < ymax:            
                
                z = zmin
                
                while z < zmax:                
                    
                    pt = (x, y, z)                
                    
                    if CSGobj.contains(pt):
                        origin = (pt[0]-pex[0]/2, pt[1]-pex[1]/2, pt[2]-pex[2]/2)
                        extent = (pt[0]+pex[0]/2, pt[1]+pex[1]/2, pt[2]+pex[2]/2)
                        voxel = Geo.Box(origin=origin, extent=extent)
                        self.addCSGvoxel(voxel, colour=colour, opacity=1., material=material)                
                    
                    z = z + res*(zmax-zmin)

                y = y + res*(ymax-ymin)

            x = x + res*(xmax-xmin)     

        print('Complete.')

    def addCSGvoxel(self, box, colour, material=None, opacity=1.):
        """
        16/03/10: To visualise CSG objects
        """
           
        if colour is None:
            colour = visual.color.red
            
        org = box.origin
        ext = box.extent
            
        size = np.abs(ext - org)
            
        pos = org + 0.5*size                      
            
        visual.box(pos=pos, size=size, color=colour, opacity=opacity, material=material)
        
    def addPhoton(self, photon):
        """
        Draws a smallSphere with direction arrow and polarisation (if data is available).
        """
        self.addSmallSphere(photon.position)
        visual.arrow(pos=photon.position, axis=photon.direction * 0.0005, shaftwidth=0.0003,
                     color=visual.color.magenta, opacity=0.8)
        if photon.polarisation is not None:
            visual.arrow(pos=photon.position, axis=photon.polarisation * 0.0005, shaftwidth=0.0003,
                         color=visual.color.white, opacity=0.4)
        
    def addObject(self, obj, colour=None, opacity=0.5, res=0.01, material=None):
        """
        Translates Scene's geometry elements into CSG elements for visualizer

        :param obj: object to draw (link to the "real"object used in simulation_
        :param colour: display color
        :param opacity: opacity
        :param res: resolution
        :param material: material
        :return: None
        """
        if not Visualiser.VISUALISER_ON:
            return
        if isinstance(obj, Geo.Box):
            self.addBox(obj, colour=colour, material=material, opacity=opacity)
        if isinstance(obj, Geo.Ray):
            self.addRay(obj, colour=colour, material=material, opacity=opacity)
        if isinstance(obj, Geo.Cylinder):
            self.addCylinder(obj, colour=colour, material=material, opacity=opacity)
        if isinstance(obj, Geo.FinitePlane):
            self.addFinitePlane(obj, colour, opacity, material=material)
        if isinstance(obj, Csg.CSGadd) or isinstance(obj, Csg.CSGint) or isinstance(obj, Csg.CSGsub):
            self.addCSG(obj, res, origin, extent, colour, material=material, opacity=opacity)
        if isinstance(obj, Geo.Polygon):
            self.addPolygon(obj, colour=colour, material=material, opacity=opacity)
        if isinstance(obj, Geo.Sphere):
            self.addSphere(obj, colour=colour, material=material, opacity=opacity)
