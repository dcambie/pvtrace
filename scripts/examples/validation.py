from __future__ import division
import numpy as np
import sys
#import logging
from pvtrace.external import transformations as tf
from pvtrace import *
import time


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
config = {}
config['log_file']              = 'simulation.log'      # Location of log file
config['db_file']               = 'pvtracedb.sql'       # Database file (with pvtracedb.sql overwriting is forced)
config['source']                = 'LED1.txt'            # Lightsource spectrum file (AM1.5g-full.txt for sun)
config['photons_to_throw']      = 500                 # Number of photons to be simulated
# Logging
config['debug']                 = False                 # Debug output (implies informative output)
config['informative_output']    = True                 # Print informative outpout (implies print summary)
config['print_waveleghts']      = False                 # Wavelenght of photons in channels
config['print_summary']         = False                  # tab-separated summary data (For ease Excel import)
# Visualizer parameters
config['visualizer']            = True                  # VPython
config['show_lines']            = True                  # Ray lines rendering
config['show_path']             = True                  # Photon path rendering
# Device Data
config['L']                     = 0.05                  # Length    (5 cm)
config['W']                     = 0.05                  # Width     (5 cm)
config['H']                     = 0.006                 # Thickness (6 mm 0.2+0.4)
# Channels
config['cL']                    = 0.05                  # Length    (5 cm)
config['cW']                    = 0.001                 # Width     (.8mm)
config['cH']                    = 0.001                 # Heigth    (.1mm)
config['cdepth']                = 0.002                 # Depth of channels in waveguide (from bottom) [MUST be lower than H+cH
config['shape']                 = "box"                 # Either box or cylinder
config['cStartX']               = 0                     # Starting X coord for channels (default 0.0064)
config['cStartY']               = 0.025                 # Starting Y coord for channels (default 0.005)
config['cnum']                  = 1                     # Number of channels (26)
config['cspacing']              = 0.0012                # Spacing between channels (0.0012)
config['reaction_mixture_re']   = 1.42                  # Reaction mixture's refractive index (1.33)
config['transmittance_at_peak'] = 0.0362                # Trasmission at absorbance peak, matches experimental (for lsc whose height is H)
config['mb_conc']               = 0.0012                # Molar concentratin mb in channels
# Device Parameters
config['bilayer']               = False                 # Simulate bilayer system?
config['transparent']           = False                 # Simulate transparent device (negative control)
config['bottom_reflector']      = True                  # Use bottom reflector (white paper, scattering only) EXPERIMENTAL
config['side_reflectors']       = True                  # Use side reflectors on edges (3M reflective adhesive foil) EXPERIMENTAL
# PovRay rendering
config['render_hi_quality']     = False                 # Hi-quality PovRay Render of the scene
config['render_low_quality']    = False                 # Fast PovRay Render of the scene

#  TMP overwrite
#config['cW'] = 0.0005
#config['cH'] = 0.0005
#config['H'] = 0.005
#config['cnum'] = 50
#config['cdepth'] = 0.0025
#config['cspacing'] = 0.0005
#config['bilayer'] = True
#config['visualizer'] = True
#config['photons_to_throw'] = 1
#config['informative_output'] = True
#config['show_lines'] = True
#config['show_path']  = True  
#config['debug'] = True
config['transmittance_at_peak'] = 0.001
config['source'] = 'AM1.5g-full.txt'
#config['shape']  = "box"

#logging.basicConfig(filename=config['log_file'],level=logging.DEBUG)
PVTDATA = '/home/dario/pvtrace/data/'

# Random seed (with the same seed same random photons will be generated, this can be usefull in some comparisons)
random_seed = int(time.time())

if config['debug']:
    config['informative_output'] = true
if config['informative_output']:
    config['print_summary'] = True
    
#if config['informative_output']:
    #print "##### PVTRACE CONFIG REPORT #####"
    #for key in sorted(config.iterkeys()):
        #line = '{:>25}  {:>2}  {:>20}'.format(key, "->", config[key])
        #print line
    #print "\n"

file = os.path.join(PVTDATA,'sources',config['source'])
oriel = load_spectrum(file, xbins=np.arange(400,800))
source = PlanarSource(direction=(0,0,-1), spectrum=oriel, length=config['L'], width=config['W']) # Incident light (perpendicular to device)
source.translate((0,0,0.05)) # Distance from device is z-H

# 3a) Load dye absorption and emission data (Red305)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt')
abs = load_spectrum(file)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red-fit.ems.txt')
ems = load_spectrum(file)


# Put header here just if needed (other output on top)
header = "Thrown\tReflected (top)\tLost bottom\tLuminescent out at edges\tLuminescent out top/bottom\tChannels_direct\tChannels_luminescent\tNonRadiative"
if config['print_summary'] == True and config['informative_output'] == False :
    print header

# start main cycle for batch simulations
for i in range(1,2):
    if config['informative_output']:
        print "##### PVTRACE CONFIG REPORT #####"
        for key in sorted(config.iterkeys()):
            line = '{:>25}  {:>2}  {:>20}'.format(key, "->", config[key])
            print line
        print "\n"
    
    # Variable distance
    #config['cspacing'] = 0.004+0.001*i
    #config['cnum'] = int(math.floor(0.050/(config['cH']+config['cspacing'])))
    #t_need = 0.01-0.001*i
    #H = 0.0055 - 0.0005*i
    #cdepth = H-0.001
    #print "******************************\n *** thickness *** ",H
    
    # 3b) Adjust concenctration
    absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt'))
    # Absorption peak
    ap = absorption_data[:,1].max()
    # Correcting factor to adjust absorption at peak to match settings
    phi = -1/(ap*(config['H'])) * np.log(config['transmittance_at_peak'])
    absorption_data[:,1] = absorption_data[:,1]*phi
    
    if config['informative_output']:
        print "Absorption data scaled to peak, ", absorption_data[:,1].max()
        print "Therefore transmission at peak = ", np.exp(-absorption_data[:,1].max() * config['H'])

    absorption = Spectrum(x=absorption_data[:,0], y=absorption_data[:,1])
    emission_data = np.loadtxt(os.path.join(PVTDATA,"dyes", 'fluro-red-fit.ems.txt'))
    emission = Spectrum(x=emission_data[:,0], y=emission_data[:,1])

    # 3c) Create material
    fluro_red = Material(absorption_data=absorption, emission_data=emission, quantum_efficiency=0.95, refractive_index=1.5)
    # 4) Give the material a linear background absorption (pmma)
    abs = Spectrum([0,1000], [2,2])
    ems = Spectrum([0,1000], [0.1,0]) # Giving emission suppress error. It's btw not used due to quantum_efficiency=0 :)
    pdms = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.41)
    
    # 5) Make the LSC and give it both dye and pmma materials
    lsc = LSC(origin=(0,0,0), size=(config['L'],config['W'],config['H']))
    
    # Trasparent is used to compare with a non-doped 
    if config['transparent']:
        lsc.material = pdms
    else:
        lsc.material = CompositeMaterial([pdms, fluro_red], refractive_index=1.41, silent=True)
    
    lsc.name = "LSC"
    scene = Scene()
    scene.add_object(lsc)
    
    # 6) Make channel within LSC and try to register to scene
    abs = Spectrum([0,1000], [2,2])
    ems = Spectrum([0,1000], [0,0])
    
    # From http://omlc.org/spectra/mb/mb-water.html
    mb_absorption_data = np.loadtxt(os.path.join(PVTDATA, 'dyes', 'MB_abs.txt'))
    # Convert in m-1 (as in Materials.py:185)
    mb_phi = 100*2.303*config['mb_conc']
    mb_absorption_data[:,1] = mb_absorption_data[:,1]*mb_phi
    mb_spectrum = Spectrum(x=mb_absorption_data[:,0], y=mb_absorption_data[:,1])
    #reaction_mixture = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.44)
    reaction_mixture = Material(absorption_data=mb_spectrum, emission_data=ems, quantum_efficiency=0.0, refractive_index=config['reaction_mixture_re'])

    channels = []
    for i in range(0, config['cnum']):
        #shape is cylinder or box
        channels.append(Channel(origin=(config['cStartX'],config['cStartY']+((config['cW']+config['cspacing'])*i),config['cdepth']), size=(config['cL'],config['cW'],config['cH']),shape=config['shape']))
        channels[i].material = reaction_mixture
        channels[i].name = "Channel"+str(i)

    if config['bilayer']:
        for i in range(0, config['cnum']-1):
            channels.append(Channel(origin=(config['cStartX'],config['cStartY']+((config['cW']+config['cspacing'])*i)+(config['cW']+config['cspacing'])/2,config['cdepth']-0.001), size=(config['cL'],config['cW'],config['cH'])))
            channels[i+config['cnum']].material = reaction_mixture
            channels[i+config['cnum']].name = "Channel"+str(i+config['cnum'])

    for channel in channels:
        scene.add_object(channel)
    if config['bottom_reflector']:
        reflector = PlanarReflector(reflectivity=0.8, origin=(0,0,-0.003), size=(config['L'],config['W'],0.002))
        reflector.name = "White_Paper"
        scene.add_object(reflector)

    if config['render_hi_quality']:
        scene.pov_render(camera_position = (0,0,0.1), camera_target = (0.025,0.025,0), height = 2400, width =3200)
    if config['render_low_quality']:
        scene.pov_render(camera_position = (0,0,0.1), camera_target = (0.025,0.025,0), height = 300, width =600)

    # Ask python that the directory of this script file is and use it as the location of the database file
    pwd = os.getcwd()
    dbfile = os.path.join(pwd, config['db_file']) # <--- the name of the database file

    trace = Tracer(scene=scene, source=source, seed=random_seed, throws=config['photons_to_throw'], database_file=dbfile, use_visualiser=config['visualizer'], show_log=config['debug'], show_axis=True)
    trace.show_lines = config['show_lines']
    trace.show_path  = config['show_path']
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
    sys.stdout.flush()
    
    if config['informative_output']:
        print "##### PVTRACE LOG RESULTS #####"
        import subprocess
        label = subprocess.check_output(["git", "describe"], cwd=PVTDATA)
        print "PvTrace ",label
        import time
        print "Date/Time",time.strftime("%c")
        print "Run Time: ", toc - tic," sec.(s)"
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
    if config['debug']:
        print "objects with record", trace.database.objects_with_records()
        print "surface with records", trace.database.surfaces_with_records()

    photons = trace.database.uids_in_reactor()
    photons_in_channels_tot = len(photons)
    luminescent_photons_in_channels = len(trace.database.uids_in_reactor_and_luminescent())
    # oNLY PHOTONS IN CHANNELS!
    for photon in photons:
        if config['debug']:
            print "Wavelenght: ",trace.database.wavelengthForUid(photon)# Nice output
        elif config['print_waveleghts']:
            print " ".join(map(str,trace.database.wavelengthForUid(photon) )) # Clean output (for elaborations)

    if config['debug']:
        print channel.name," photons: ",photons_in_channels_tot/thrown * 100,"% (",photons_in_channels_tot,")"

    if config['informative_output']:
        print "Photons in channels (sum)",photons_in_channels_tot/thrown * 100,"% (",photons_in_channels_tot,")"
    
    # Put header here just if needed (other output on top)
    if config['print_summary'] == True and config['informative_output'] == True :
        print header
    if config['print_summary']:
        top_reflected = len(trace.database.uids_out_bound_on_surface("top", solar=True))
        bottom_lost = len(trace.database.uids_out_bound_on_surface("bottom", solar=True))
        print thrown,"\t",top_reflected,"\t",bottom_lost,"\t",luminescent_edges,"\t",luminescent_apertures,"\t",(photons_in_channels_tot-luminescent_photons_in_channels),"\t",luminescent_photons_in_channels,"\t",non_radiative_photons
    
    if config['debug']:#Check coherence of results
        if top_reflected+bottom_lost+luminescent_edges+luminescent_apertures+photons_in_channels_tot+non_radiative_photons == thrown:
            print "Results validity check OK :)"
        else:
            print "!!! ERROR !!! Check results carefully!"
    
sys.exit(0)
