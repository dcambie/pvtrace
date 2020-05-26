pvtrace - Optical ray tracing for photovoltaic devices and luminescent materials
-------

The master branch of this repo will be kept frozen as it is referenced in the Electronic Supporting Information of "Every photon counts: understanding and optimizing photon paths in luminescent solar concentrator-based photomicroreactors (LSC-PMs)" DOI: [10.1039/C7RE00077D](https://doi.org/10.1039/C7RE00077D) Reaction Chemistry & Engineering 4, 2017.

Thanks to Federica De Chiara for highlighting this issue.
 

pvtrace was originally written to simulate luminescent solar concentrators during my PhD studies. However it has grown into a much more powerful tool, capable of optical ray tracing complicated structures, and the collection of statistical data to enable characterisation of optics useful for photovoltaics and solar energy conversion.

If you use pvtrace please use the following citation,

> Daniel J Farrell, *"pvtrace: optical ray tracing for photovoltaic devices and luminescent materials"*,  http://dx.doi.org/10.5281/zenodo.12820

Overview of features:
* Constructive Solid Geometry
* Generalised 3D ray intersections (ray optics):
  - ray-box
  - ray-cylinder
  - ray-CSG object
* Arbitrary 3D object transformations:
  - translation
  - rotation
  - scaling and skewing
* Photon path visualiser
* Statistical collection of photonic properties:
  - wavelength
  - direction
* Automatic Fresnel reflection and refraction
* Sampling from statistical distributions:
  - optical absorption coefficient
  - emission spectrum
  - wavelength and angular reflectivity

pvtrace is written entirely in Python. Using the numpy library. This was chosen to emphasis rapid development, learning and collaboration rather than speed of execution. On a single core machine pvtrace takes a few minutes to produce sensible results which for me is an acceptable trade-off considering the pleasure it was to write in Python!

Authors:
Daniel J Farrell -- Original author and benevolent dictator
Carl Poelking -- Constructive Solid Geometry
Karl C Godel -- Convex objects, Faces, and Polygons
Markus Fuhrer -- povray scene rendering and multiprocessing
Amanda Chatten -- Windows friendly
Dario Cambié -- LSC-PM adjustments

Installation:

For detailed installation instructions see the wiki,
http://github.com/danieljfarrell/pvtrace/wiki



