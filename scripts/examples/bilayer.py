from __future__ import division
import numpy as np
import sys
import logging
from pvtrace.external import transformations as tf
from pvtrace import *

''' Simulation of a rectangular homogeneously doped LSC
Steps:
1) Define parameters
2) Create light source
3) Load absorption and emission data for orgnaic dye
4) Load linear background absorption for PDMS
5) Create LSC object and start tracer
6) Calculate statistics
'''

# Simulation
log_file    = 'simulation.log'  # Location of log file
db_file     = 'pvtracedb.sql'   # Database file (with pvtracedb.sql overwriting is forced)
source      = 'LED1.txt'        # Lightsource spectrum file (AM1.5g-full.txt for sun)
photons_to_throw = 10000        # Number of photons to be simulated
# Logging
debug                   = False # Debug output (implies informative output)
informative_output      = False # Print informative outpout (implies print summary)
print_wavelehgt_channels= False # Wavelenght of photons in channels
print_summary           = True  # tsv summary data
# Visualizer parameters
visualizer = False              # VPython
show_lines = False              # Ray lines rendering
show_path  = False              # Photon path rendering
# Device Data
L = 0.07                        # Length    (7 cm)
W = 0.06                        # Width     (6 cm)
H = 0.005                       # Thickness (5 mm)
# Channels
cL = 0.05                       # Length    (5 cm)
cW = 0.0008                     # Width     (.8mm)
cH = 0.0001                     # Heigth    (.1mm)
cdepth   = 0.004                # Depth of channels in waveguide (from bottom) [MUST be lower than H+cH
cnum     = 26                   # Number of channels
cspacing = 0.0012               # Spacing between channels
rmix_re  = 1.33                 # Reaction mixture's refractive index
t_need      = 0.0362            # Trasmission at absorbance peak, matches experimental (for lsc whose height is H)
# Device Parameters
bilayer     = False             # Simulate bilayer system?
transparent = False              # Simulate transparent device (negative control)
# PovRay rendering
render_hi_quality  = False      # Hi-quality PovRay Render of the scene
render_low_quality = False      # Fast PovRay Render of the scene

#  TMP overwrite
cW = 0.0005
cH = 0.0005
H = 0.0025
#bilayer = True
cspacing = 0.0005
#visualizer = true
#photons_to_throw = 10
cnum = 50
cdepth = 0.0015
transparent = True

logging.basicConfig(filename=log_file,level=logging.DEBUG)

import time
random_seed = int(time.time())# Random seed (with the same seed same random photons will be generated, this can be usefull in some comparisons)

if debug:
    informative_output = true
if informative_output:
    print_summary = True

# 2) Create light source, truncate to 400 -- 800nm range
#file = os.path.join(PVTDATA,'sources','AM1.5g-full.txt')
file = os.path.join(PVTDATA,'sources',source)
oriel = load_spectrum(file, xbins=np.arange(400,800))
source = PlanarSource(direction=(0,0,-1), spectrum=oriel, length=L, width=W) # Incident light (perpendicular to device)
source.translate((0,0,0.05)) # Distance from device is z-H

# 3a) Load dye absorption and emission data (Red305)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt')
abs = load_spectrum(file)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red-fit.ems.txt')
ems = load_spectrum(file)

# Put header here just if needed (other output on top)
header = "Thrown\tReflected (top)\tLost bottom\tLuminescent out at edges\tLuminescent out top/bottom\tChannels_direct\tChannels_luminescent\tNonRadiative"
if print_summary == True and informative_output == False :
    print header

# start main cycle for batch simulations
for i in range(1,10):
    #t_need = 0.01-0.001*i
    #H = 0.0055 - 0.0005*i
    #cdepth = H-0.001
    #print "******************************\n *** thickness *** ",H
    
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
    # 4) Give the material a linear background absorption (pmma)
    abs = Spectrum([0,1000], [2,2])
    ems = Spectrum([0,1000], [0,0]) # Giving emission suppress error. It's btw not used due to quantum_efficiency=0 :)
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

    trace = Tracer(scene=scene, source=source, seed=random_seed, throws=photons_to_throw, database_file=dbfile, use_visualiser=visualizer, show_log=debug, show_axis=False)
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

    luminescent_edges = len(trace.database.uids_out_bound_on_surface('left', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('right', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('near', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('far', luminescent=True)) # Photons on edges are only luminescent with planarsource perpendicular to device, so luminescent=true not really needed in *THIS* case
    luminescent_apertures = len(trace.database.uids_out_bound_on_surface('top', luminescent=True)) + len(trace.database.uids_out_bound_on_surface('bottom', luminescent=True))
    non_radiative_photons = len(trace.database.uids_nonradiative_losses())
    
    if informative_output:
        print ""
        print "Run Time: ", toc - tic
        print ""
        
        print "Technical details:"
        print "\t Generated \t", generated
        print "\t Killed \t", killed
        print "\t Thrown \t", thrown
        
        print "Summary:"
        print "\t Optical efficiency \t", luminescent_edges * 100 / thrown, "%"
        print "\t Photon efficiency \t", (luminescent_edges + luminescent_apertures) * 100 / thrown, "%"
        
        print "Luminescent photons:"

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']

        for surface in edges:
            print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"

        for surface in apertures:
            print "\t", surface, "\t", len(trace.database.uids_out_bound_on_surface(surface, luminescent=True))/thrown * 100, "%"

        print "Non radiative losses\t", non_radiative_photons/thrown * 100, "%"

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
    photons_in_channels_tot = len(photons)
    luminescent_photons_in_channels = len(trace.database.uids_in_reactor_and_luminescent())
    for photon in photons:
        if debug:
            print "Wavelenght: ",trace.database.wavelengthForUid(photon)# Nice output
        elif print_wavelehgt_channels:
            print trace.database.wavelengthForUid(photon) # Clean output (for elaborations)

    if debug:
        print channel.name," photons: ",photons_in_channels_tot/thrown * 100,"% (",photons_in_channels_tot,")"

    if informative_output:
        print "Photons in channels (sum)",photons_in_channels_tot/thrown * 100,"% (",photons_in_channels_tot,")"
    
    # Put header here just if needed (other output on top)
    # FIX LOSS-FLUORESCENT AND ADD TOP ADN BOTTOM
    if print_summary == True and informative_output == True :
        print header
    if print_summary:
        top_reflected = len(trace.database.uids_out_bound_on_surface("top", solar=True))
        bottom_lost = len(trace.database.uids_out_bound_on_surface("bottom", solar=True))
        print thrown,"\t",top_reflected,"\t",bottom_lost,"\t",luminescent_edges,"\t",luminescent_apertures,"\t",(photons_in_channels_tot-luminescent_photons_in_channels),"\t",luminescent_photons_in_channels,"\t",non_radiative_photons
    
    if debug:#Check coherence of results
        if top_reflected+bottom_lost+luminescent_edges+luminescent_apertures+photons_in_channels_tot+non_radiative_photons == thrown:
            print "Results validity check OK :)"
        else:
            print "!!! ERROR !!! Check results carefully!"
    
sys.exit(0)
