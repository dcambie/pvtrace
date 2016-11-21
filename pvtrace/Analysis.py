from __future__ import division, print_function

from pvtrace import PhotonDatabase

import logging
import os

import matplotlib.pyplot as plt
import numpy as np

import six
import sys

if sys.version_info > (2, 7):
    plt.switch_backend('Qt5Agg')
"""
Changing the backend is important on Windows, since the default one results in the following error:
PyEval_RestoreThread: NULL tstate

That error could be circumvented calling .quit() and .destroy() on the graph element.
Using Qt4 as backend requires PyQt4 but keeps the code platform independent without inflating platform-specific code
"""


class Analysis(object):
    """
    Class for analysis of results, based on the produced database.
    Can also be applied to old database data

    Idea: just use uuid and save everything in that folder,
    given uuid the class loads previous results if folder exists nad create the folder if not
    """

    def __init__(self, database=None, uuid=None):
        self.working_dir = None
        if database is not None:
            self.db = database
            self.db_stats()

        if uuid is not None:
            self.uuid = uuid
            self.working_dir = os.path.join(os.path.expanduser('~'), 'pvtrace_data', self.uuid)
            self.graph_dir = os.path.join(self.working_dir, 'graphs')
            try_db_location = os.path.join(self.working_dir, "db.sqlite")
            if database is None and os.access(try_db_location, os.R_OK):
                self.db = PhotonDatabase.PhotonDatabase(dbfile=try_db_location, readonly=True)
            
        self.log = logging.getLogger('pvtrace.analysis')
        self.photon_generated = None
        self.photon_killed = None
        self.tot = None
        self.non_radiative = None

    def add_db(self, database):
        self.db = database

    def db_stats(self):
        self.photon_generated = len(self.db.uids_generated_photons())
        self.photon_killed = len(self.db.killed())
        self.tot = self.photon_generated - self.photon_killed
        self.non_radiative = len(self.db.uids_nonradiative_losses())

    def percent(self, num_photons):
        """
        Return the percentage of num_photons with respect to thrown photons as 2 decimal digit string
        :param num_photons: number of photons to be divided by the total
        :rtype: string
        """
        # This needs "from __future__ import division"
        assert self.tot > 0, "Total photons are zero"
        return format((num_photons / self.tot) * 100, '.2f') + ' % (' + str(num_photons).rjust(6, ' ') + ' )'

    def print_detailed(self):
        """
        Prints a detailed report on the fate of the photons stored in self.db

        :return:None
        """
        # Todo: here and in print_excel several totals are computed twice. Consider moving common code in other function
        self.db_stats()

        self.log.debug('Print_detailed() called on DB with ' + str(self.photon_generated) + ' photons')

        # print('obj ', self.db.objects_with_records())
        # print('surfaces ', self.db.surfaces_with_records())

        self.log.info("Technical details:")
        self.log.info("\t Generated \t" + str(self.photon_generated))
        self.log.info("\t Killed \t" + str(self.photon_killed))
        self.log.info("\t Thrown \t" + str(self.tot))

        self.log.info("Luminescent photons:")

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']
        faces = edges + apertures

        luminescent = 0
        for surface in faces:
            photons = len(self.db.uids_out_bound_on_surface(surface, luminescent=True))
            self.log.info("\t" + surface + "\t" + self.percent(photons))
            luminescent += photons

        self.log.info("Non radiative losses\t" + self.percent(self.non_radiative))
        self.log.info("Solar photons:")

        solar = 0
        for surface in apertures:
            photons = len(self.db.uids_out_bound_on_surface(surface, solar=True))
            self.log.info("\t" + surface + "\t" + self.percent(photons))
            solar += photons

        self.log.info("Reactor's channel photons:")
        photons_in_channels_luminescent = len(self.db.uids_in_reactor_and_luminescent())
        photons_in_channels_tot = len(self.db.uids_in_reactor())
        photons_in_channels_direct = photons_in_channels_tot - photons_in_channels_luminescent

        self.log.info("Photons in channels (direct)\t" + self.percent(photons_in_channels_direct))
        self.log.info("Photons in channels (luminescent)\t" + self.percent(photons_in_channels_luminescent))
        self.log.info("Photons in channels (sum)\t" + self.percent(photons_in_channels_tot))

        if solar + luminescent + self.non_radiative + photons_in_channels_tot == self.tot:
            self.log.info("Results sanity check OK!")
        else:
            self.log.warn("Results FAILED sanity check!!!")

    def print_wavelength_channels(self, only_luminescent=True):
        """
        Prints the wavelengths of the photons absorbed by the channels.

        :param only_luminescent: Boolean, if true returns only the luminescent photons, if false also solar ones
        :return: csv string with headers
        """
        self.log.debug("Print_wavelength_channels called")
        if only_luminescent:
            ret_str = " Photons in reactor (luminescent only). Wavelengths in nm"
            for photon in self.db.uids_in_reactor_and_luminescent():
                ret_str += " ".join(map(str, self.db.wavelength_for_uid(photon)))  # Clean output (for elaborations)
        else:
            ret_str = " Photons in reactor (all). Wavelengths in nm"
            for photon in self.db.uids_in_reactor():
                ret_str += " ".join(map(str, self.db.wavelength_for_uid(photon)))  # Clean output (for elaborations)

        return ret_str

    def print_excel_header(self, additional=None):
        """
        Column header for print_excel()
        """
        if additional is None:
            r_text = "Generated, Killed, Total, Losses, Luminescent - Left, Luminescent - Near, Luminescent - Far, " \
                   "Luminescent - Right, Luminescent - Top, Luminescent - Bottom, Solar - Top, Solar - Bottom, " \
                   "Channels - Direct, Channels - Luminescent"
        else:
            r_text = additional+", Generated, Killed, Total, Losses, Luminescent - Left, Luminescent - Near," \
                              "Luminescent - Far, Luminescent - Right, Luminescent - Top, Luminescent - Bottom," \
                              "Solar - Top, Solar - Bottom, Channels - Direct, Channels - Luminescent"
        self.log.info(r_text)
        return r_text

    def print_excel(self, additions=None):
        """
        Prints an easy to import report on the fate of the photons stored in self.db
        """
        self.db_stats()
        if additions is None:
            return_text = ''
        else:
            return_text = str(additions) + ", "
        # GENERATED
        return_text += str(self.photon_generated) + ", "
        # KILLED
        return_text += str(self.photon_killed) + ", "
        # THROWN (GENERATED-KILLED)
        return_text += str(self.tot) + ", "
        # NON RADIATIVE LOSSES
        return_text += str(self.non_radiative) + ", "

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']
        faces = edges + apertures

        # LUMINESCENT: left, near, far, right, top, bottom
        luminescent_surfaces = 0
        for surface in faces:
            photons = len(self.db.uids_out_bound_on_surface(surface, luminescent=True))
            luminescent_surfaces += photons
            return_text += str(photons) + ", "

        # SOLAR: top and bottom
        for surface in apertures:
            return_text += str(len(self.db.uids_out_bound_on_surface(surface, solar=True))) + ", "

        luminescent_photons_in_channels = len(self.db.uids_in_reactor_and_luminescent())
        photons_in_channels_tot = len(self.db.uids_in_reactor())

        # CHANNELS: direct
        return_text += str(photons_in_channels_tot - luminescent_photons_in_channels) + ", "
        # CHANNELS: luminescent
        return_text += str(luminescent_photons_in_channels)

        self.log.info(return_text)
        return return_text

    def get_bounces(self, photon_list=None):
        """
        Average number of bounces per luminescent photon

        :param photon_list: array with uids of photons of interest (they are assumed to be fluorescent)
        :return:
        """
        bounces = []
        for photon in photon_list:
            bounces.append(self.db.bounces_for_uid(photon)[0])

        y = np.bincount(bounces)
        x = np.linspace(0, max(bounces), num=max(bounces) + 1)
        return x, y

    def history_from_pid(self, pid=None):
        # FIXME : this is still missing
        pass

    def history_from_uid(self, uid=None):
        """
        Extract from the DB the trace of the given photon uid.
        If a list of uids is provided it's split into individual traces

        :param uid: list uid of photon to be investigated
        """
        # FIXME: account for photon lists!
        if uid is None:
            return False
        else:
            return self.history_from_pid(self.db.pid_from_uid(uid))

    def create_graphs(self, prefix=''):
        """
        Generate a series of graphs on photons stored in self.db

        :param prefix:
        :return:
        """
        self.log.debug("Analysis.create_graphs() called with prefix=" + prefix)

        if hasattr(self, 'uuid'):
            prefix = self.graph_dir
            try:
                os.stat(prefix)
            except OSError:
                os.mkdir(prefix)

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']

        uids_luminescent_sum_edges = []
        for surface in edges:
            uids_luminescent_sum_edges += self.db.uids_out_bound_on_surface(surface, luminescent=True)

        uids_luminescent_sum_apertures = []
        for surface in apertures:
            uids_luminescent_sum_apertures += self.db.uids_out_bound_on_surface(surface, luminescent=True)

        graphs = {
            'reactor-total': self.db.uids_in_reactor(),
            'reactor-luminescent': self.db.uids_in_reactor_and_luminescent(),
            'lsc-edges': uids_luminescent_sum_edges,
            'lsc-apertures': uids_luminescent_sum_apertures,
            'lsc-reflected': self.db.uids_out_bound_on_surface('top', solar=True),
            'lsc-transmitted': self.db.uids_out_bound_on_surface('bottom', solar=True)}

        # noinspection PyCompatibility
        for plot, uid in six.iteritems(graphs):
            if len(uid) < 10:
                self.log.info('[' + plot + "] The database doesn't have enough photons to generate this graph!")
            else:
                data = self.db.wavelength_for_uid(uid)
                file_path = os.path.join(prefix, plot)
                histogram(data=data, filename=file_path)
                self.log.info('[' + plot + "] Plot saved to " + file_path)

        self.log.info("Plotting bounces luminescent to channels")
        uids = self.db.uids_in_reactor_and_luminescent()
        if len(uids) < 10:
            self.log.info("[bounces channel] The database doesn't have enough photons to generate this graph!")
        else:
            data = self.get_bounces(photon_list=uids)
            file_path = os.path.join(prefix, 'bounces channel')
            xyplot(x=data[0], y=data[1], filename=file_path)
            self.log.info("[bounces channel] Plot saved to " + file_path)

        uids = self.db.uids_luminescent()
        if len(uids) < 10:
            self.log.info("[bounces channel] The database doesn't have enough photons to generate this graph!")
        else:
            pass
            # data = self.get_bounces(photon_list=uids)
            # xyplot(x=data[0], y=data[1], filename=os.path.join(prefix, 'bounces_all'))

    def save_db(self, location=None):
        self.db.dump_to_file(location)


# fixme: move this to Spectrum
def histogram(data, filename, wavelength_range=(350, 700)):
    """
    Create an histogram with the cumulative frequency of photons at different wavelength

    :param data: List with photons' wavelengths
    :param filename: Filename for the exported file. Will be saved in home/pvtrace_export/filenam (+.png appended)
    :param wavelength_range : range of wavelength to be plotted (X axis)
    """

    home = os.path.expanduser('~')
    if filename.find(home) != -1:
        saving_location = filename
    else:
        saving_location = os.path.join(home, "pvtrace_export", filename)
    suffixes = ('png', 'pdf')

    # print "histogram called with ",data
    # hist = np.histogram(data, bins=100, range=range)
    # hist = np.histogram(data, bins=np.linspace(400, 800, num=101))
    # print "hist is ",hist
    if wavelength_range is None:
        plt.hist(data, histtype='stepfilled')
    else:
        plt.hist(data, np.linspace(wavelength_range[0], wavelength_range[1], num=101), histtype='stepfilled')
    for extension in suffixes:
        location = saving_location + "." + extension
        plt.savefig(location)
        os.chmod(location, 0o777)
    plt.clf()


def xyplot(x, y, filename):
    """
    Plots a curve in a cartesian graph

    :rtype: None
    :param x: X axis (typically nm for Abs/Ems)
    :param y: Y axis (e.g. Abs or intensity)
    :param filename: Graph filename for disk saving
    """

    home = os.path.expanduser('~')
    if filename.find(home) != -1:
        saving_location = filename
    else:
        saving_location = os.path.join(home, "pvtrace_export", filename)
    suffixes = ('png', 'pdf')

    plt.scatter(x, y, linewidths=1)
    plt.plot(x, y, '-')
    for extension in suffixes:
        location = saving_location + "." + extension
        plt.savefig(location)
        os.chmod(location, 0o777)
        print('Plot saved in ', location, '!')
    plt.clf()