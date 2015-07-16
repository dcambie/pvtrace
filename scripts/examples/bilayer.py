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

# Parameters

db_file     = 'pvtracedb.sql'   # Database file (with this name forces overwrite....)
photon_file = 'data.photons'    # Stores wavelenght of photons in channels
source      = 'LED1.txt'        # Lightsource spectrum file
t_need      = 0.0362            # Trasmission at absorbance peak, matches experimental (for lsc whose height is H)
rmix_re     = 1.33              # Reaction mixture, ACN/H2O 4:1

photons_to_throw = 10000        # Number of photons to be simulated
bilayer     = False             # Simulate bilayer system?
transparent = False             # Simulate transparent device (negative control)
rmix_re     = 1.33              # Reaction mixture's refractive index

informative_output = True       # Print informative outpout
print_wavelehgt_channels = False# Wavelenght of photons in channels
debug = False                   # Debug output

visualizer = False              # VPython
show_lines = False              # Ray lines rendering
show_path  = False              # Photon path rendering

render_hi_quality = False
render_low_quality = False

# 1) Define some sizes (arbitrary used 1=1m)
# device size
L = 0.07      # 7 cm
W = 0.06      # 6 cm
H = 0.005     # 5 mm

# channel size
cL = 0.05         # 5cm
cW = 0.0008       # 800um
cH = 0.0001       # 100um
cdepth = 0.004    # depth of channels in waveguide
cnum = 26         # number of channels
cspacing = 0.0012 # spacing between channels

# 2) Create light source from AM1.5 data, truncate to 400 -- 800nm range
#file = os.path.join(PVTDATA,'sources','AM1.5g-full.txt')
file = os.path.join(PVTDATA,'sources',source)
oriel = load_spectrum(file, xbins=np.arange(400,800))
source = PlanarSource(direction=(0,0,-1), spectrum=oriel, length=L, width=W) # Incident light AM1.5g spectrum
source.translate((0,0,0.05))

# 3a) Load dye absorption and emission data
file = os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt')
abs = load_spectrum(file)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red-fit.ems.txt')
ems = load_spectrum(file)

for i in range(1,10):
    t_need = 0.01-(0.001*i)
    print "******************************\n *** TRASMITTANCE *** ",t_need
    
    
    # 3b) Adjust concenctration
    absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt'))
    ap = absorption_data[:,1].max()
    phi = -1/(ap*(H)) * np.log(t_need)
    absorption_data[:,1] = absorption_data[:,1]*phi

    if informative_output:
        print "Absorption data scaled to peak, ", absorption_data[:,1].max()
        print "Therefore transmission at peak = ", np.exp(-absorption_data[:,1].max() * H)

    absorption = Spectrum(x=absorption_data[:,0], y=absorption_data[:,1])
    emission_data = np.loadtxt(os.path.join(PVTDATA,"dyes", 'fluro-red-fit.ems.txt'))
    emission = Spectrum(x=emission_data[:,0], y=emission_data[:,1])

    # 3c) Create material
    fluro_red = Material(absorption_data=absorption, emission_data=emission, quantum_efficiency=0.95, refractive_index=1.5)
    #fluro_red = Material(absorption_data=absorption, emission_data=emission, quantum_efficiency=0.0, refractive_index=1.5)

    # 4) Give the material a linear background absorption (pmma)
    abs = Spectrum([0,1000], [2,2])
    ems = Spectrum([0,1000], [0,0])
    pdms = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.41)

    # 5) Make the LSC and give it both dye and pmma materials
    lsc = LSC(origin=(0,0,0), size=(L,W,H))

    # Trasparent is used to compare with a non-doped 
    if transparent:
        lsc.material = pdms
    else:
        lsc.material = CompositeMaterial([pdms, fluro_red], refractive_index=1.41, silent=True)

    lsc.name = "LSC"
    scene = Scene()
    scene.add_object(lsc)

    # 6) Make channel within LSC and try to register to scene
    abs = Spectrum([0,1000], [0.3,0.3])
    ems = Spectrum([0,1000], [0,0])
    #reaction_mixture = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.44)
    reaction_mixture = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=rmix_re)
    #channel.material = SimpleMaterial(reaction_mixture)

    channels = []
    for i in range(0, cnum-1):
        channels.append(Channel(origin=(0.0064,0.005+((cW+cspacing)*i),cdepth), size=(cL,cW,cH)))
        channels[i].material = reaction_mixture
        channels[i].name = "Channel"+str(i)

    if bilayer:
        for i in range(0, cnum-2):
            channels.append(Channel(origin=(0.0064,0.005+((cW+cspacing)*i)+(cW+cspacing)/2,cdepth-0.001), size=(cL,cW,cH)))
            channels[i+cnum-1].material = reaction_mixture
            channels[i+cnum-1].name = "Channel"+str(i+cnum)

    for channel in channels:
        scene.add_object(channel)

    if render_hi_quality:
        scene.pov_render(camera_position = (0,0,0.1), camera_target = (0.025,0.025,0), height = 2400, width =3200)
    if render_low_quality:
        scene.pov_render(camera_position = (0,0,0.1), camera_target = (0.025,0.025,0), height = 300, width =600)

    # Ask python that the directory of this script file is and use it as the location of the database file
    pwd = os.getcwd()
    dbfile = os.path.join(pwd, db_file) # <--- the name of the database file

    trace = Tracer(scene=scene, source=source, seed=1, throws=photons_to_throw, database_file=dbfile, use_visualiser=visualizer, show_log=debug, show_axis=False)
    trace.show_lines = show_lines
    trace.show_path  = show_path
    import time
    tic = time.clock()
    trace.start()
    #trace.stop()
    toc = time.clock()

    # 6) Statistics
    generated = len(trace.database.uids_generated_photons())
    killed = len(trace.database.killed())
    thrown = generated - killed

    if informative_output:
        print ""
        print "Run Time: ", toc - tic
        print ""
        
        print "Technical details:"
        print "\t Generated \t", generated
        print "\t Killed \t", killed
        print "\t Thrown \t", thrown
        
        print "Summary:"
        print "\t Optical efficiency \t", (len(trace.database.uids_out_bound_on_surface('left', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('right', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('near', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('far', luminescent=True))) * 100 / thrown, "%"
        print "\t Photon efficiency \t", (len(trace.database.uids_out_bound_on_surface('left')) + len(trace.database.uids_out_bound_on_surface('right')) + len(trace.database.uids_out_bound_on_surface('near')) + len(trace.database.uids_out_bound_on_surface('far')) + len(trace.database.uids_out_bound_on_surface('top')) + len(trace.database.uids_out_bound_on_surface('bottom'))) * 100 / thrown, "%"
        
        print "Luminescent photons:"

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']

        for surface in edges:
            print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"

        for surface in apertures:
            print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"

        print "Non radiative losses\t", len(trace.database.uids_nonradiative_losses())/thrown * 100, "%"

        print "Solar photons (transmitted/reflected):"
        for surface in edges:
            print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, solar=True))/thrown * 100, "%"

        for surface in apertures:
            print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, solar=True))/thrown * 100, "%"

        print "Reactor's channel photons:"

    # LOG
    if debug:
        print "objects with record", trace.database.objects_with_records()
        print "surface with records", trace.database.surfaces_with_records()

    photons = trace.database.uids_in_reactor()

    for photon in photons:
        if debug:
            print "Wavelenght: ",trace.database.wavelengthForUid(photon)# Nice output
        elif print_wavelehgt_channels:
            print trace.database.wavelengthForUid(photon) # Clean output (for elaborations)

    photon_count = len(photons)
    if debug:
        print channel.name," photons: ",photon_count/thrown * 100,"% (",photon_count,")"

    if informative_output:
        print "Photons in channels (sum)",photon_count/thrown * 100,"% (",photon_count,")"
        
sys.exit(0)
