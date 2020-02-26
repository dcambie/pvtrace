from pvtrace.geometry.cylinder import Cylinder
from pvtrace.geometry.mesh import Mesh
from pvtrace.material.distribution import Distribution
from pvtrace.scene.node import Node
from pvtrace.scene.scene import Scene
from pvtrace.scene.renderer import MeshcatRenderer
from pvtrace.geometry.sphere import Sphere
from pvtrace.material.dielectric import Dielectric, LossyDielectric
from pvtrace.light.light import Light
from pvtrace.algorithm import photon_tracer

import time
import random
import numpy as np
import trimesh
import logging
import json

logging.getLogger('pvtrace').setLevel(logging.CRITICAL)
logging.getLogger('trimesh').setLevel(logging.CRITICAL)
logging.getLogger('matplotlib').setLevel(logging.CRITICAL)


# UNITS ARE METERS!
NUM_PHOTONS = 50000
vial_length = 0.180
vial_diameter = 0.018
bottom_space = 0.001
led_distance = 0.0065


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
vial_body.rotate(np.radians(-90), [1, 0, 0])

# VIAL RMIX BOTTOM
rmix_bottom = Node(
    name="Rmix bottom",
    geometry=Sphere(
        radius=_vial_radius*0.8,
        material=LossyDielectric.make_constant((400.0, 500.0), 1.3, 1000.0)
    ),
    parent=vial_bottom
)

# VIAL RMIX BODY
rmix_body = Node(
    name="Vial body",
    geometry=Cylinder(
        length=_cylinder_length,
        radius=_vial_radius*0.8,
        material=LossyDielectric.make_constant((400.0, 500.0), 1.3, 1000.0)
    ),
    parent=vial_body
)
# rmix_body.rotate(angle=math.pi/2, axis=[1, 0, 0])

# Mesh
reflector = Node(
    name="mesh (icosahedron)",
    geometry=Mesh(
        trimesh=trimesh.load("test.stl"),
        material=Dielectric.make_constant(x_range=(400, 500), refractive_index=0)
    ),
    parent=world
)
# Align bottom
reflector.location = (0, 0, 0.125/2)

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
exit_rays = []

start_time = time.time()
count = 0
for ray in led.emit(NUM_PHOTONS):
    # Do something with the photon trace information...
    info = photon_tracer.follow(ray, scene)
    rays, events = zip(*info)

    count += 1

    # Add rays to the renderer (optional)
    if count % 100 == 0:
        viewer.add_ray_path(rays)
        print(count)

    try:
        exit_rays.append(rays[-3])  # -1 and -2 are the world node, don't want that
    except IndexError:
        pass
print(f"Total time is {(time.time()-start_time):.1f} s")

# Open the scene in a new browser window (optional)
viewer.render(scene)

reaction = 0
for ray in exit_rays:
    if rmix_body.geometry.contains(ray.representation(from_node=world, to_node=rmix_body).position):
        reaction += 1
    if rmix_bottom.geometry.contains(ray.representation(from_node=world, to_node=rmix_bottom).position):
        reaction += 1

print(f"I have {reaction} ({(reaction*100/NUM_PHOTONS):.1f}%) photons in the reaction mixture!")

# Save to JSON
add = {bottom_space: reaction/NUM_PHOTONS}
with open('results.json') as f:
    data = json.load(f)

data.update(add)

with open('results.json', 'w') as f:
    json.dump(data, f)


# Keep the script alive until Ctrl-C (optional)
while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        break
