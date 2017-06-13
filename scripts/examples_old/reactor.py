from __future__ import division
import numpy as np
import sys
from pvtrace.external import transformations as tf
from pvtrace import *

''' Simulation of a rectangular homogeneously doped LSC

Steps:
1) Define sizes
2) Create a light source
3) Load absorption and emission data for orgnaic dye
4) Load linear background absorption for PMMA
5) Create LSC object and start tracer
6) Calculate statistics.

'''

# 1) Define some sizes
L = 0.05
W = 0.05
H = 0.005

cL = 0.03
cW = 0.001
cH = 0.001

# 2) Create light source from AM1.5 data, truncate to 400 -- 800nm range
file = os.path.join(PVTDATA,'sources','AM1.5g-full.txt')
oriel = load_spectrum(file, xbins=np.arange(400,800))
source = PlanarSource(direction=(0,0,-1), spectrum=oriel, length=L, width=W) # Incident light AM1.5g spectrum
source.translate((0,0,0.05))

# 3a) Load dye absorption and emission data
file = os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt')
abs = load_spectrum(file)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red-fit.ems.txt')
ems = load_spectrum(file)

# 3b) Adjust concenctration
absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt'))
T_need = 0.05 # Want to transmit 5% of the light at the peak absorption wavelength
t_need = 0.0362
ap = absorption_data[:,1].max()
phi = -1/(ap * H) * np.log(T_need)
phi *= 1
absorption_data[:,1] = absorption_data[:,1]*phi
print "Absorption data scaled to peak, ", absorption_data[:,1].max()
print "Therefore transmission at peak = ", np.exp(-absorption_data[:,1].max() * H)

absorption = Spectrum(x=absorption_data[:,0], y=absorption_data[:,1])
emission_data = np.loadtxt(os.path.join(PVTDATA,"dyes", 'fluro-red-fit.ems.txt'))
emission = Spectrum(x=emission_data[:,0], y=emission_data[:,1])

# 3c) Create material
fluro_red = Material(absorption_data=absorption, emission_data=emission, quantum_efficiency=0.95, refractive_index=1.5)

# 4) Give the material a linear background absorption (pmma)
abs = Spectrum([0,1000], [2,2])
ems = Spectrum([0,1000], [0,0])
pdms = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.41)

# 5) Make the LSC and give it both dye and pmma materials
lsc = LSC(origin=(0,0,0), size=(L,W,H))
lsc.material = CompositeMaterial([pdms, fluro_red], refractive_index=1.41)
lsc.name = "LSC"
scene = Scene()
scene.add_object(lsc)

# 6) Make channel within LSC and try to register to scene
abs = Spectrum([0,1000], [0.3,0.3])
ems = Spectrum([0,1000], [0,0])
reaction_mixture = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.44)
#channel.material = SimpleMaterial(reaction_mixture)
cdepth = 0.0005
channel1 = RayBin(origin=(0.01,0.01,cdepth), size=(cL,cW,cH))
channel1.material=reaction_mixture
channel1.name="Channel1"
channel2 = RayBin(origin=(0.01,0.015,cdepth), size=(cL,cW,cH))
channel2.material=reaction_mixture
channel2.name="Channel2"
channel3 = RayBin(origin=(0.01,0.020,cdepth), size=(cL,cW,cH))
channel3.material=reaction_mixture
channel3.name="Channel3"
channel4 = RayBin(origin=(0.01,0.025,cdepth), size=(cL,cW,cH))
channel4.material=reaction_mixture
channel4.name="Channel4"
channel5 = RayBin(origin=(0.01,0.030,cdepth), size=(cL,cW,cH))
channel5.material=reaction_mixture
channel5.name="Channel5"
channel6 = RayBin(origin=(0.01,0.035,cdepth), size=(cL,cW,cH))
channel6.material=reaction_mixture
channel6.name="Channel6"

#channel.material = reaction_mixture
#channel.name = "Channel1"
scene.add_object(channel1)
scene.add_object(channel2)
scene.add_object(channel3)
scene.add_object(channel4)
scene.add_object(channel5)
scene.add_object(channel6)

scene.pov_render(camera_position = (0,0,0.1), camera_target = (0.025,0.025,0), height = 400, width = 600)

# Ask python that the directory of this script file is and use it as the location of the database file
pwd = os.getcwd()
dbfile = os.path.join(pwd, 'reactor_db.sql') # <--- the name of the database file


trace = Tracer(scene=scene, source=source, seed=1, throws=250, database_file=dbfile, use_visualiser=True)
trace.show_lines = True
trace.show_path = True
import time
tic = time.clock()
trace.start()
toc = time.clock()

# 6) Statistics
print ""
print "Run Time: ", toc - tic
print ""

print "Technical details:"
generated = len(trace.database.uids_generated_photons())
killed = len(trace.database.killed())
thrown = generated - killed
print "\t Generated \t", generated
print "\t Killed \t", killed
print "\t Thrown \t", thrown

print "Summary:"
print "\t Optical efficiency \t", (len(trace.database.uids_out_bound_on_surface('left', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('right', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('near', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('far', luminescent=True))) * 100 / thrown, "%"
print "\t Photon efficiency \t", (len(trace.database.uids_out_bound_on_surface('left')) + len(trace.database.uids_out_bound_on_surface('right')) + len(trace.database.uids_out_bound_on_surface('near')) + len(trace.database.uids_out_bound_on_surface('far')) + len(trace.database.uids_out_bound_on_surface('top')) + len(trace.database.uids_out_bound_on_surface('bottom'))) * 100 / thrown, "%"

print "Luminescent photons:"
edges = ['left', 'near', 'far', 'right']
apertures = ['top', 'bottom']
r_edges = ['r_left', 'r_near', 'r_far', 'r_right']
r_apertures = ['r_top', 'r_bottom']

for surface in edges:
    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"

for surface in apertures:
    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"


#print "Reactor's luminescent photons:"
#for surface in r_edges:
#    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"

#for surface in r_apertures:
#    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"


print "Non radiative losses\t", len(trace.database.uids_nonradiative_losses())/thrown * 100, "%"

print "Solar photons (transmitted/reflected):"
for surface in edges:
    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, solar=True))/thrown * 100, "%"

for surface in apertures:
    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, solar=True))/thrown * 100, "%"

print "Reactor's channel photons:"
#for surface in r_edges:
#    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, solar=True))/thrown * 100, "%"

#for surface in r_apertures:
#    print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, solar=True))/thrown * 100, "%"

#trace.database
#print "objects with record", trace.database.objects_with_records()
#print "surface with records", trace.database.surfaces_with_records()
c1=len(trace.database.endpoint_uids_for_object("Channel1"))
c2=len(trace.database.endpoint_uids_for_object("Channel2"))
c3=len(trace.database.endpoint_uids_for_object("Channel3"))
c4=len(trace.database.endpoint_uids_for_object("Channel4"))
c5=len(trace.database.endpoint_uids_for_object("Channel5"))
c6=len(trace.database.endpoint_uids_for_object("Channel6"))

print "photons on channel #1", c1/thrown * 100, "%"
print "photons on channel #2", c2/thrown * 100, "%"
print "photons on channel #3", c3/thrown * 100, "%"
print "photons on channel #4", c4/thrown * 100, "%"
print "photons on channel #5", c5/thrown * 100, "%"
print "photons on channel #6", c6/thrown * 100, "%"
print "Photons in channels (sum)", (c1+c2+c3+c4+c5+c6)/thrown * 100, "%"


sys.exit()
