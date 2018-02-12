from pvtrace.Devices import Channel
from pvtrace.Materials import Spectrum, Material, SimpleMaterial


class Capillary(object):
    """Class for a capillary, i.e. tubing + reaction mixture channel"""
    def __init__(self, axis_origin=(0, 0, 0), axis=0, length=1, outer_diameter=0.0015875, inner_diameter=0.000750,
                 tubing="PFA", reaction_material=SimpleMaterial(555), refractive_index_cg=1.340):
        # fixed by chong to solve the bug of the same face on two objects
        epi = 10**-6
        axis_o = list(axis_origin)
        axis_fixbug = [0, epi, 0]
        axis_rea = []
        for x,y in zip(axis_o, axis_fixbug):
            axis_rea.append(x+y)
        axis_reaction = tuple(axis_rea)
        # all done

        outer_radius = outer_diameter/2
        inner_radius = inner_diameter/2
        # This could be easily rewritten in a shorter way but this is imho more clear
        if axis == 0:
            tubing_outer_size = (length, outer_radius, outer_radius)
            tubing_inner_size = (length - 2*epi, inner_radius, inner_radius)
        elif axis == 1:
            tubing_outer_size = (outer_radius, length, outer_radius)
            tubing_inner_size = (inner_radius, length - 2*epi, inner_radius)
        elif axis == 2:
            tubing_outer_size = (outer_radius, outer_radius, length)
            tubing_inner_size = (inner_radius, inner_radius, length - 2*epi)
        else:
            raise ValueError("Invalid axis ("+str(axis)+")provided to capillary!")



        self.tubing = Channel(origin=axis_origin, size=tubing_outer_size, shape="cylinder")
        self.reaction = Channel(origin=axis_reaction, size=tubing_inner_size, shape="cylinder")

        emission = Spectrum([0, 1000], [0.1, 0])
        if tubing == "PFA":  # high-purity PFA, "normal" PFA is 1.35
            absorbance = Spectrum([0, 1000], [0.1, 0])  # FIXME Polymer transmittance data needed!
            tubing_material = Material(absorption_data=absorbance, emission_data=emission, quantum_efficiency=0.0,
                                       refractive_index=refractive_index_cg) # original version is 1.340
        elif tubing == "HALAR":
            absorbance = Spectrum([0, 1000], [0.1, 0])  # FIXME Polymer transmittance data needed!
            tubing_material = Material(absorption_data=absorbance, emission_data=emission, quantum_efficiency=0.0,
                                       refractive_index=1.447)
        elif tubing == "TEFZEL":
            absorbance = Spectrum([0, 1000], [0.1, 0])  # FIXME Polymer transmittance data needed!
            tubing_material = Material(absorption_data=absorbance, emission_data=emission, quantum_efficiency=0.0,
                                       refractive_index=1.40)
        else:
            raise NotImplementedError("The material specified for the tubing ("+polymer+") is unknown!")

        # Materials
        self.reaction.material = reaction_material
        self.tubing.material = tubing_material