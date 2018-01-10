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

import logging
# try:
# import scipy as sp
# from scipy import interpolate
# except Exception as exception:
#    try:
#        print "SciPy not installed."
#        import interpolate
#    except Exception as exception:
#        print exception
#        print "It seems that you don't have interpolate... bugger... Python FAIL."

from pvtrace.Geometry import *
from pvtrace.Interpolation import Interp1d, BilinearInterpolation
from pvtrace.ConstructiveGeometry import CSGadd, CSGint, CSGsub
from pvtrace.external.transformations import translation_matrix, rotation_matrix
import pvtrace.external.transformations as tf
import math
from types import *
import os


def load_spectrum(filename, xbins=None, base10=True):
    assert os.path.exists(filename), "File '%s' does not exist." % filename
    spectrum = Spectrum(filename=filename, base10=base10)

    # Truncate the spectrum using the xbins
    return spectrum if xbins is None else Spectrum(x=xbins, y=spectrum(xbins), base10=base10)
    # Note: Spectrum instances are callable thanks to the __call__ decorator of the Spectrum class ;)


def common_abscissa(a, b):
    la = len(a)
    lb = len(b)

    if la <= lb:
        tmp = a
        a = b
        b = tmp

    i = 0
    j = 0
    c = []

    while i < la:
        if a[i] < b[j]:
            c.append(float(a[i]))
            if i + 1 < la:
                i += 1
            else:
                break
        elif a[i] > b[j]:
            c.append(float(b[j]))
            if j + 1 < lb:
                j += 1
            else:
                break
        else:
            # c.append(float(a[i]))
            i += 1

    return c


def wav2RGB(wavelength):
    """
    Credits: Dan Bruton
    See: http://codingmess.blogspot.com/2009/05/conversion-of-wavelength-in-nanometers.html
    """
    w = int(wavelength)

    # colour
    if 380 <= w < 440:
        red = -(w - 440.) / (440. - 350.)
        green = 0.0
        blue = 1.0
    elif 440 <= w < 490:
        red = 0.0
        green = (w - 440.) / (490. - 440.)
        blue = 1.0
    elif 490 <= w < 510:
        red = 0.0
        green = 1.0
        blue = -(w - 510.) / (510. - 490.)
    elif 510 <= w < 580:
        red = (w - 510.) / (580. - 510.)
        green = 1.0
        blue = 0.0
    elif 580 <= w < 645:
        red = 1.0
        green = -(w - 645.) / (645. - 580.)
        blue = 0.0
    elif 645 <= w <= 780:
        red = 1.0
        green = 0.0
        blue = 0.0
    else:
        red = 0.0
        green = 0.0
        blue = 0.0

    # intensity correction
    if 380 <= w < 420:
        sss = 0.3 + 0.7 * (w - 350) / (420 - 350)
    elif 420 <= w <= 700:
        sss = 1.0
    elif 700 < w <= 780:
        sss = 0.3 + 0.7 * (780 - w) / (780 - 700)
    else:
        sss = 0.0
    sss *= 255

    return [int(sss * red), int(sss * green), int(sss * blue)]


def fresnel_reflection(incident_angle, n1, n2):
    assert 0.0 <= incident_angle <= 0.5 * np.pi, "Incident angle must be between 0 and 90 degrees" \
                                                 "to calculate Fresnel reflection."
    # Catch TIR case
    if n2 < n1:
        if incident_angle > np.arcsin(n2 / n1):
            return 1.0

    Rs1 = n1 * np.cos(incident_angle) - n2 * np.sqrt(1 - (n1 / n2 * np.sin(incident_angle)) ** 2)
    Rs2 = n1 * np.cos(incident_angle) + n2 * np.sqrt(1 - (n1 / n2 * np.sin(incident_angle)) ** 2)
    Rs = (Rs1 / Rs2) ** 2
    Rp1 = n1 * np.sqrt(1 - (n1 / n2 * np.sin(incident_angle)) ** 2) - n2 * np.cos(incident_angle)
    Rp2 = n1 * np.sqrt(1 - (n1 / n2 * np.sin(incident_angle)) ** 2) + n2 * np.cos(incident_angle)
    Rp = (Rp1 / Rp2) ** 2
    return 0.5 * (Rs + Rp)


def fresnel_reflection_with_polarisation(normal, direction, polarisation, n1, n2):
    # Catch TIR case
    if n2 < n1:
        if angle(normal, direction) > np.arcsin(n2 / n1):
            return 1.0

    rads = angle(normal, direction)
    Rs1 = n1 * np.cos(rads) - n2 * np.sqrt(1 - (n1 / n2 * np.sin(rads)) ** 2)
    Rs2 = n1 * np.cos(rads) + n2 * np.sqrt(1 - (n1 / n2 * np.sin(rads)) ** 2)
    Rs = (Rs1 / Rs2) ** 2
    Rp1 = n1 * np.sqrt(1 - (n1 / n2 * np.sin(rads)) ** 2) - n2 * np.cos(rads)
    Rp2 = n1 * np.sqrt(1 - (n1 / n2 * np.sin(rads)) ** 2) + n2 * np.cos(rads)
    Rp = (Rp1 / Rp2) ** 2

    # Catch the normal incidence case
    if rads == 0.:
        # The reflection is independent of polarisation in this case
        return 0.5 * (Rs + Rp)

    # Calculate the weighting factor between TM (-p polarised) and TE (-s polarised) components
    # The normal vector of the plane of incidence
    n_p = norm(np.cross(direction, reflect_vector(normal, direction)))
    # Scalar magnitude of the projection of the polarisation vector on the the plane of incidence
    phi_p = np.sin(np.arccos(np.dot(n_p, norm(polarisation))))
    # i.e. how much of the electric field is in the plane of incidence
    return (1 - phi_p) * Rs + phi_p * Rp


def fresnel_refraction(normal, vector, n1, n2):
    n = n1 / n2
    dot = np.dot(norm(vector), norm(normal))
    c = np.sqrt(1 - n ** 2 * (1 - dot ** 2))
    sign = 1
    if dot < 0.0:
        sign = -1
    refraction = n * vector + sign * (c - sign * n * dot) * normal
    return norm(refraction)


class Spectrum(object):
    """
    A class that represents a spectral quantity

    e.g. absorption, emission or refractive index spectrum as a function of wavelength in nanometers.
    """

    def __init__(self, x=None, y=None, filename=None, base10=True):
        """
        Initialised with x and y which are array-like data of the same length. x must have units of wavelength
        (that is in nanometers), y can an arbitrary units. However, if the Spectrum is representing an
        absorption coefficient y must have units of (1/m).
        :rtype: object
        """
        super(Spectrum, self).__init__()

        if filename is not None:

            try:
                data = np.loadtxt(filename)
            except Exception as e:
                print("Failed to load data from file, %s", str(filename))
                print(e)
                exit(1)

            self.x = np.array(data[:, 0], dtype=np.float32)
            self.y = np.array(data[:, 1], dtype=np.float32)

            # Sort array based on ASC X if needed
            arr1inds = self.x.argsort()
            self.x = self.x[arr1inds[::1]]
            self.y = self.y[arr1inds[::1]]

        elif x is not None and y is not None:
            self.x = np.array(x, dtype=np.float32)
            self.y = np.array(y, dtype=np.float32)

        else:
            # We need to make some data up -- i.e. flat over the full model range
            self.x = np.array([200, 500, 750, 4000], dtype=np.float32)
            self.y = np.array([0, 0, 0, 0], dtype=np.float32)

        if len(self.x) == 0:
            # We need to make some data up -- i.e. flat over the full model range
            self.x = np.array([200, 500, 750, 4000], dtype=np.float32)
            self.y = np.array([0, 0, 0, 0], dtype=np.float32)

        elif len(self.x) == 1:
            # We have a harder time at making up some data
            xval = self.x[0]
            yval = self.y[0]
            bins = np.arange(np.floor(self.x[0] - 1), np.ceil(self.x[0] + 2))
            indx = np.where(bins == xval)[0][0]
            self.x = np.array(bins, dtype=np.float32)
            self.y = np.zeros(len(self.x), dtype=np.float32)
            self.y[indx] = np.array(yval, dtype=np.float32)

        # Check for negative values
        for y in self.y:
            assert float(y) >= 0, "Spectrum has negative values!"

        if base10:
            self.y *= 1/np.log10(math.e)
        # Make the 'spectrum'
        self.spectrum = Interp1d(self.x, self.y, bounds_error=False, fill_value=0.0)

        # Make the pdf for wavelength lookups
        try:
            # Convert the (x,y) point pairs to a histogram of bins and frequencies
            bins = np.hstack([self.x, 2 * self.x[-1] - self.x[-2]])
        except IndexError:
            print("Index Error from array, ", self.x)

        cdf = np.cumsum(self.y)
        if not (max(cdf) == 0):
            pdf = cdf / max(cdf)
            pdf = np.hstack([0, pdf[:]])
            self.pdf_lookup = Interp1d(bins, pdf, bounds_error=False, fill_value=0.0)
            self.pdfinv_lookup = Interp1d(pdf, bins, bounds_error=False, fill_value=0.0)

    def __call__(self, nanometers):
        """
        Returns the values of the Spectrum at the 'nanometers' value(s).

        An number is returned if nanometers is a number,
        A numpy array is returned if nanometers if a list of a numpy array.
        """
        # Check is the nanometers is a number
        b1 = True if isinstance(nanometers, float) else False
        b2 = True if isinstance(nanometers, int) else False
        b3 = True if isinstance(nanometers, np.float32) else False
        b4 = True if isinstance(nanometers, np.float64) else False

        if b1 or b2 or b3 or b4:
            return np.float(self.value(nanometers))
        return self.value(nanometers)

    def value(self, nanometers):
        """
        Returns the value of the spectrum at the specified wavelength

        If the wavelength is outside the data range zero is returned.
        """
        return self.spectrum(nanometers)

    def probability_at_wavelength(self, nanometers):
        """
        Returns the probability associated with the wavelength.

        This is found by computing the cumulative probability function of the spectrum which is unique for each value
        for non-zero y values.
        If the wavelength is below the data range zero is returned, and if above one is returned.
        """
        if nanometers > self.x.max():
            return 1.0
        else:
            return self.pdf_lookup(nanometers)

    def wavelength_at_probability(self, probability):
        """
        Returns the wavelength associated with the specified probability.

        This is found by computing the inverse cumulative probability function (see probability_at_wavelength).
        The probability must be between zero and one (inclusive) otherwise a value error exception is raised.
        """
        if 0 <= probability <= 1:
            return self.pdfinv_lookup(probability)
        else:
            raise ValueError('A probability must be between 0 and 1 inclusive')

    def write(self, filename=None):
        if file is not None:
            data = np.zeros((len(self.x), 2))
            data[:, 0] = self.x
            data[:, 1] = self.y
            np.savetxt(filename, data)

    def __add__(self, other):
        if other is None:
            return self
        common_x = common_abscissa(self.x, other.x)
        new_y = self.value(common_x) + other.value(common_x)
        return Spectrum(common_x, new_y)

    def __sub__(self, other):
        if other is None:
            return self
        common_x = common_abscissa(self.x, other.x)
        new_y = self.value(common_x) - other.value(common_x)
        return Spectrum(common_x, new_y)

    def __mul__(self, other):
        if other is None:
            return self
        common_x = common_abscissa(self.x, other.x)
        new_y = self.value(common_x) * other.value(common_x)
        return Spectrum(common_x, new_y)

    def __div__(self, other):
        if other is None:
            return self
        common_x = common_abscissa(self.x, other.x)
        new_y = self.value(common_x) / other.value(common_x)
        return Spectrum(common_x, new_y)


class AngularSpectrum(object):
    """
    A spectrum with an angular dependence.
    """
    """
    >>> x = np.array([400.,600.,601,1000.])
    >>> y = np.array([0., np.pi/4, np.pi/2])
    >>> z = np.array([[0., 0., 0.], [1e-9, 1e-9, 1e-9], [1-1e-9, 1-1e-9, 1-1e-9], [1.,1.,1.]])
    >>> z_i = BilinearInterpolation(x,y,z)
    >>> z_i(610,0.1) == 0.99999999902255665
    True
    
    """

    def __init__(self, x, y, z):
        super(AngularSpectrum, self).__init__()
        self.x = x
        self.y = y
        self.z = z
        self.spectrum = BilinearInterpolation(x, y, z, fill_value=0.0)

    def value(self, nanometers, radians):
        return self.spectrum(nanometers, radians)


class Material(object):
    """
    A material than can absorb and emit photons objects.

    A photon is absorbed if a pathlength generated by sampling the Beer-Lambert Law for the photon is less than the
    pathlength to escape the container. The emission occurs weighted by the quantum_efficiency
    (a probability from 0 to 1).
    The emission wavelength must occur at a red-shifted value with respect to the absorbed photon.
    This is achieved by sampling the emission spectrum from the photons wavelength upwards.
    The direction of the emitted photon is chosen uniformly from an isotropic distribution of angles.
    """

    def __init__(self, absorption_data=None, constant_absorption=None, emission_data=None, quantum_efficiency=0.0,
                 refractive_index=1.0):
        """
        Creates a material

        :param absorption_data: a Spectrum object, with units 1/m/nm
        :param constant_absorption: alternative to spectrum if absorption is constant
        :param emission_data: a Spectrum object with units 1/nm
        :param quantum_efficiency: optional argument (probability of emission) If 0.0 the emission_spectrum is None
        :param refractive_index: refractive index of material. Also check CompositeMaterial
        :return:
        """

        super(Material, self).__init__()

        # --- 
        def spectrum_from_data_source(data_source):

            if isinstance(data_source, str):
                if os.path.isfile(data_source):
                    data = np.loadtxt(data_source)
                    return Spectrum(x=data[:, 0], y=data[:, 1])
                else:
                    raise IOError("File '%s' does not exist at this location, '%s' .")\
                          % (os.path.basename(data_source), data_source)

            # Data is 'list-like'
            elif isinstance(data_source, list) or isinstance(data_source, tuple) or isinstance(data_source, np.ndarray):

                rows, cols = np.shape(data_source)
                assert rows > 1, "Error processing the data file '%s'." \
                                 "PVTrace data files need at least 2 rows and must have 2 columns." \
                                 "This data file has %d rows and %d columns." % (data_source, rows, cols)
                assert cols == 2, "Error processing the data file '%s'." \
                                  "PVTrace data files need at least 2 rows and must have 2 columns." \
                                  "This data file has %d rows and %d columns." % (data_source, rows, cols)
                return Spectrum(x=data_source[:, 0], y=data_source[:, 1])

            # Data is already a spectrum
            elif isinstance(data_source, Spectrum):
                return data_source

            else:
                raise IOError("PVTrace cannot process %s input given to the Material object."
                              "Please use the location of a text file (UTF-8 format) which contains spectral data"
                              "as 2 columns of increasing wavelength (col#1 is the wavelength; col#2 is data).")

        # ---

        # Load absorption data
        if constant_absorption is not None:
            # Load linear background absorption
            self.constant_absorption = constant_absorption
            self.absorption_data = Spectrum(x=[200, 4000], y=[constant_absorption, constant_absorption])

        elif absorption_data is None:
            # No data given -- make if False (used just for BOUNDS)
            # self.absorption_data = Spectrum(x=[0, 4000], y=[0, 0])
            self.absorption_data = False

        else:
            self.absorption_data = spectrum_from_data_source(absorption_data)

        # Load spectral emission data
        if emission_data is None:
            # Flat emission profile
            self.emission_data = Spectrum(x=[200, 4000], y=[1, 1])

        else:
            self.emission_data = spectrum_from_data_source(emission_data)

        # Load quantum efficiency
        assert 0 <= quantum_efficiency <= 1, "Quantum efficiency is  outside the 0 to 1 range."
        self.quantum_efficiency = quantum_efficiency

        # Load refractive index
        assert refractive_index >= 1, "Refractive index is less than 1.0"
        self.refractive_index = refractive_index

    def absorption(self, photon):
        """
        Returns the absorption coefficient experienced by the photon.
        """
        if not self.absorption_data:
            return False

        if self.absorption_data.value(photon.wavelength) > 0:
            return self.absorption_data.value(photon.wavelength)
        return 10e-30

    def emission_direction(self):
        """
        Returns a 3 component direction vector with is chosen isotropically.

        ..note:: This method is overridden by subclasses to provide custom emission
        direction properties.
        """

        # This method of calculating isotropic vectors is taken from GNU Scientific Library
        LOOP = True
        while LOOP:
            x = -1. + 2. * np.random.uniform()
            y = -1. + 2. * np.random.uniform()
            s = x ** 2 + y ** 2
            if s <= 1.0:
                LOOP = False

        z = -1. + 2. * s
        a = 2 * np.sqrt(1 - s)
        x *= a
        y *= a
        return np.array([x, y, z])

    def emission_wavelength(self, photon):
        """Returns a new emission wavelength for the photon."""
        # The emitted photon must be red-shifted to conservation of energy
        lower_bound = self.emission_data.probability_at_wavelength(photon.wavelength)
        return self.emission_data.wavelength_at_probability(np.random.uniform(lower_bound, 1.))

    def emission(self, photon):
        """Updates the photon with a new wavelength and direction, assuming it has been absorbed and emitted."""

        # Update wavelength
        photon.wavelength = self.emission_wavelength(photon)

        # Update direction
        photon.direction = self.emission_direction()
        return photon

    def trace(self, photon, free_pathlength):
        """
        Trace the photon through the material

        Will apply absorption and emission probabilities to the photon along its free path in the present geometrical
        container and return the result photon for tracing. The free_pathlength is the distance travelled in metres
        until the photon reaches the edge of the present container. It is for the calling object to decided how to
        proceed with the returned photon. For example, if the returned photon is in the volume of the container the
        same tracing procedure should be applied.
        However, if the photon reaches a face, reflection, refraction calculation should be applied etc.
        If the photon is lost, the photons active instance variables is set to False.
        It is for the calling object to check this parameter and act accordingly
        e.g. recording the lost photon and great a new photon to trace.
        """

        # Clear state using for collecting statistics
        photon.absorber_material = None
        photon.emitter_material = None

        # This is True just for BOUNDS and prevent division by zero warning
        if not self.absorption_data:
            photon.position = photon.position + free_pathlength * photon.direction
            return photon
        # Assuming the material has a uniform absorption coefficient we generated a random path length
        # weighed by the material absorption coefficient.
        sampled_pathlength = -np.log(1 - np.random.uniform()) / self.absorption(photon)

        # Photon absorbed.
        if sampled_pathlength < free_pathlength:

            # Move photon to the absorption location
            photon.material = self
            photon.position += sampled_pathlength * photon.direction
            photon.absorption_counter += 1

            # Photon emitted.
            if np.random.uniform() < self.quantum_efficiency:
                photon.reabs += 1
                return self.emission(photon)

            # Photon not emitted.
            else:
                photon.active = False
                return photon

        # Photon not absorbed
        else:
            # Move photon along path
            photon.position = photon.position + free_pathlength * photon.direction
            return photon


class CompositeMaterial(Material):
    """
    A material that is composed from a homogeneous mix of multiple materials.

    For example, a plastic plate doped with a blue and red absorbing dyes has the absorption coefficient of plastic as
    well as the absorption and emission properties of the dyes.
    """

    def __init__(self, materials, refractive_index=None):
        """Initialised by a list or array of material objects."""
        super(CompositeMaterial, self).__init__()
        self.materials = materials
        if refractive_index is None:
            print("")
            print("CompositeMaterial must be created with a value of refractive index which is an estimate of the"
                  "effective medium of all materials which it contains. The individual refractive index of each"
                  "material is ignored when grouping multiple material together using a composite material.\n")
            print("For example try using, CompositeMaterial([pmma, dye1, dye2], refractive_index=1.5]).\n")
            raise ValueError
        self.refractive_index = refractive_index
        # These parameters are dynamically set to those of the relative material within self.trace()
        self.emission = None
        self.absorption = None
        self.quantum_efficiency = None
        self.log = logging.getLogger('pvtrace.compositeMaterial')

    def all_absorption_coefficients(self, nanometers):
        """Returns and array of all the the materials absorption coefficients at the specified wavelength."""
        count = len(self.materials)
        # Defaults 0 for each material (fill in unexpected missing values)
        absorptions = np.zeros(count)
        # Foreach material get its absorption
        for i in range(0, count):
            absorptions[i] = self.materials[i].absorption_data.value(nanometers)
        return absorptions

    def trace(self, photon, free_pathlength):
        """
        Traces the photon in the CompositeMaterial. See the analogous behaviour in Material

        Will apply absorption and emission probabilities to the photon along its free path in the present geometrical
        container and return the result photon for tracing.
        See help(material.trace) for how this is done for a single material because the same principle applies.
        The ensemble absorption coefficient is found for the specified photon to determine if absorption occurs.
        The absorbed material itself is found at random from a distribution weighted by each of the component
        absorption coefficients.
        The resultant photon is returned with possibly a new position, direction and wavelength.
        If the photon is absorbed and not emitted the photon is returned but its active property is set to False.
        """

        # Clear state using for collecting statistics
        photon.absorber_material = None
        photon.emitter_material = None

        # print "Tracing photon into CompositeMaterial. free_pathlength:",free_pathlength*100,' cm'
        absorptions = self.all_absorption_coefficients(photon.wavelength)
        # print 'At ',photon.wavelength,' nm the absorption of the materials are:',absorptions
        absorption_coefficient = absorptions.sum()
        assert absorption_coefficient > 0, "Sum of absorption at "+str(photon.wavelength)+" nm is 0! Check emission!"
        # See WolframAlpha "-ln(1-x)/y from x=0 to 1 from y=0 to 2"
        sampled_pathlength = -np.log(1 - np.random.uniform()) / absorption_coefficient
        # print "sampled is: ",sampled_pathlength

        # Absorption occurs.
        if sampled_pathlength < free_pathlength:
            # print "photon absorbed"
            # Move photon along path to the absorption point
            photon.absorption_counter += 1
            photon.position = photon.position + sampled_pathlength * photon.direction

            # Find the absorption material
            count = len(self.materials)
            bins = range(0, count + 1)
            cdf = np.cumsum(absorptions)
            pdf = cdf / max(cdf)
            pdf = np.hstack([0, pdf[:]])
            pdfinv_lookup = Interp1d(pdf, bins, bounds_error=False, fill_value=0.0)
            absorber_index = int(np.floor(pdfinv_lookup(np.random.uniform())))
            material = self.materials[absorber_index]
            # print 'the absorber was ',absorber_index
            photon.material = material
            photon.absorber_material = material
            self.emission = material.emission
            self.absorption = material.absorption
            self.quantum_efficiency = material.quantum_efficiency

            # Emission occurs.
            if np.random.uniform() < material.quantum_efficiency:
                self.log.debug("   *  Photon re-emitted!")
                photon.reabs += 1
                photon.emitter_material = material
                # Generates a new photon with red-shifted wavelength, new direction and polarisation
                photon = material.emission(photon)
                return photon

            else:
                self.log.debug("   *  Photon lost!")
                # Emission does not occur. Now set active = False ans return
                photon.active = False
                return photon

        else:

            # Absorption does not occur. The photon reaches the edge, update it's position and return
            photon.position = photon.position + free_pathlength * photon.direction
            return photon


def hemispherical_vector():
    LOOP = True
    while LOOP:
        x = -1. + 2. * np.random.uniform()
        y = -1. + 2. * np.random.uniform()
        s = x ** 2 + y ** 2
        if s <= 1.0:
            LOOP = False

    z = -1. + 2. * s
    a = 2 * np.sqrt(1 - s)
    x *= a
    y *= a
    return np.array([x, y, abs(z)])


class ReflectiveMaterial(object):
    """A Material that reflects photons rather an absorbing photons.
    
    Initalization:
    
    reflectivity -- A Spectrum, AngularSpectrum or number that defines the
    material reflectivity (i.e. zero to one) over the wavelength 
    range (in nanometers), and optionally over an anglular range in rads.
    
    refractive_index -- the refractive index of the coating, if unsure set to the
    refractive_index of the substrate. Or is an isolated mirrors in air set to one.
    
    lambertian -- If True then the material reflects as a Lambertian surface, other
    reflection is specular. NB This option should only be used with reflectivity=
    constant, or reflectivity=Spectrum.
    
    """

    def __init__(self, reflectivity, refractive_index=1., lambertian=False):
        super(ReflectiveMaterial, self).__init__()
        self.reflectivity = reflectivity
        self.refractive_index = refractive_index
        self.lambertian = lambertian

    def __call__(self, photon):
        """Returns the reflectivity of the coating for the incident photon."""

        if isinstance(self.reflectivity, Spectrum):
            return self.reflectivity.value(photon.wavelength)

        elif isinstance(self.reflectivity, AngularSpectrum):
            # DJF 8/5/2010
            # 
            # The internal incident angle (substate-coating) will not correspond to the same value of 
            # reflectivity as for the same angle and the external interface (air-coatings) because the 
            # refraction angle into the material will be different. We need to apply a correction factor
            # to account for this effect (see Farrell PhD Thesis, p.129, 2009)
            #
            # If the previous containing object's (i.e. this will be the substate for an internal 
            # collision, or air if an external collision) has a refractive index higher than air
            # (n_air = photon.scene.bounds.material.refractive_index) then the correction is applied,
            # else the photon must be heading into an external interface and no correction is needed.
            #
            if photon.previous_container.material.refractive_index > photon.scene.bounds.material.refractive_index:
                # Hitting internal interface, therefore apply correction to angle
                n_substrate = photon.previous_container.material.refractive_index
                n_environment = photon.scene.bounds.material.refractive_index
                rads = np.asin(n_substrate / n_environment * sin(angle(normal, photon.direction)))
            else:
                rads = angle(normal, photon.direction)

            return self.reflectivity.value(photon.wavelength, rads)

        else:
            # Assume it's a number
            return self.reflectivity

    def reflected_direction(self, photon, normal):
        """Move the photon one Monte-Carlo step forward by considering material reflections."""

        if self.lambertian:
            # Make sure that the surface normal points towards the photon
            rads = angle(normal, photon.direction)
            if rads < np.pi / 2.:
                normal *= -1.
            lambertian_emission_direction_into_positive_z = hemispherical_vector()
            rot_matrix = rotation_matrix_from_vector_alignment(np.array([0, 0, 1]), normal)
            return transform_direction(lambertian_emission_direction_into_positive_z, rot_matrix)

        return reflect_vector(normal, photon.direction)

    def trace(self, photon, free_pathlength):
        # Fake trace for ReflectiveMaterial.
        # If not reflected on interface (rare with high reflectivity) just let the photon exit on the other side
        # (that commonly means lost for any purpose)
        photon.absorber_material = None
        photon.emitter_material = None
        photon.position = photon.position + free_pathlength * photon.direction
        return photon


class SimpleMaterial(Material):
    """
    SimpleMaterial is a subclass of Material.

    It simply implements a material with a square absorption and emission spectra that slightly overlap.
    The absorption coefficient is set to 10 per metre.
    """

    def __init__(self, bandgap_nm):
        self.bandgap = bandgap_nm
        absorption_coefficient = 0.0
        absorption = Spectrum([0, bandgap_nm - 50, bandgap_nm], [absorption_coefficient, absorption_coefficient, 0.0])
        emission = Spectrum([bandgap_nm - 50, bandgap_nm, bandgap_nm + 50.], [0, 1, 0])
        super(SimpleMaterial, self).__init__(absorption_data=absorption, emission_data=emission, quantum_efficiency=1.0,
                                             refractive_index=1.0)


class SimpleMaterial2(Material):
    """
    SimpleMaterial is a subclass of Material.
    It simply implements a material with a square absorption and a triangular emission spectra that slightly overlap.
    The absorption coefficient is set to 10 per metre.
    """

    def __init__(self, bandgap_nm):
        self.bandgap = bandgap_nm
        absorption_coefficient = 2
        absorption = Spectrum([0, bandgap_nm], [absorption_coefficient, absorption_coefficient])
        Eg = bandgap_nm
        y = [0, 1, 0]
        x = [Eg - 50, Eg - 40, Eg]
        emission = Spectrum(x, y)
        super(SimpleMaterial2, self).__init__(absorption_data=absorption, emission_data=emission,
                                              quantum_efficiency=1.0, refractive_index=1.0)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
