from pvtrace.geometry.cylinder import Cylinder
from pvtrace.material.distribution import Distribution
from pvtrace.scene.node import Node
from pvtrace.scene.scene import Scene
from pvtrace.scene.renderer import MeshcatRenderer
from pvtrace.geometry.sphere import Sphere
from pvtrace.material.dielectric import Dielectric, LossyDielectric
from pvtrace.light.light import Light
from pvtrace.algorithm import photon_tracer
import time
import math
import random
import functools
import numpy as np

# UNITS ARE METERS!
vial_length = 0.180
vial_diameter = 0.018
bottom_space = 0.02
led_distance = 0.01

_cylinder_length = vial_length-vial_diameter/2
_vial_radius = vial_diameter / 2

# WORLD
world = Node(
    name="world (air)",
    geometry=Sphere(
        radius=2.0,
        material=Dielectric.air()
    )
)

# VIAL GLASS BOTTOM
vial_bottom = Node(
    name="Vial bottom",
    geometry=Sphere(
        radius=_vial_radius,
        material=Dielectric.glass()
    ),
    parent=world
)
vial_bottom.location = (0, 0, bottom_space)

# VIAL GLASS BODY
vial_body = Node(
    name="Vial body",
    geometry=Cylinder(
        length=_cylinder_length,
        radius=_vial_radius,
        material=Dielectric.glass()
    ),
    parent=world
)
vial_body.location = (0, 0, bottom_space + _cylinder_length / 2)

# VIAL RMIX BOTTOM
rmix_bottom = Node(
    name="Rmix bottom",
    geometry=Sphere(
        radius=_vial_radius*0.8,
        material=LossyDielectric.make_constant((400.0, 500.0), 1.3, 5.0)
    ),
    parent=vial_bottom
)

# VIAL RMIX BODY
rmix_body = Node(
    name="Vial body",
    geometry=Cylinder(
        length=_cylinder_length,
        radius=_vial_radius*0.8,
        material=LossyDielectric.make_constant((400.0, 500.0), 1.3, 5.0)
    ),
    parent=vial_body
)
rmix_body.rotate(angle=math.pi/2, axis=[1, 0, 0])

# CREE XP G3 Spectrum approximation
x = np.linspace(400, 500)
y = np.exp(-((x-450.0)/15.0)**2)
dist = Distribution(x, y)
dist.sample(np.random.uniform())


def led_position():
    transformations = [(led_distance, 0, 0), (0, led_distance, 0), (-led_distance, 0, 0), (0, -led_distance, 0)]
    return random.choice(transformations)

# Add source of photons
led = Light(
        wavelength_delegate=lambda: dist.sample(np.random.uniform()),
        divergence_delegate=Light.lambertian_divergence,
        position_delegate=led_position
        )
led.location = (0, 1, 0)
# led.translate((0, 1, 0))


# Use meshcat to render the scene (optional)
viewer = MeshcatRenderer(open_browser=True)
scene = Scene(world)
for ray in led.emit(50):
    # Do something with the photon trace information...
    info = photon_tracer.follow(ray, scene)
    rays, events = zip(*info)
    # Add rays to the renderer (optional)
    viewer.add_ray_path(rays)
# Open the scene in a new browser window (optional)
viewer.render(scene)

# Keep the script alive until Ctrl-C (optional)
while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        break
