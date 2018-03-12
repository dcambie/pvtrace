from __future__ import division, print_function

from pvtrace import PhotonDatabase, Trajectory

import logging
import os

import matplotlib.pyplot as plt
import numpy as np

import six
import sys
import math
import csv

if sys.version_info > (2, 7):
    plt.switch_backend('Qt5Agg')
"""
Changing the backend is important on Windows, since the default one results in the following error:
PyEval_RestoreThread: NULL tstate

That error could be circumvented calling .quit() and .destroy() on the graph element.
Using Qt5 as backend requires PyQt5 but keeps the code platform independent
"""


class Analysis(object):
    """
    Class for analysis of results, based on the produced database.
    Can also be applied to old database data (best indirectly, by creating a Scene() instance with matching uuid,
    """

    def __init__(self, database=None, uuid=None):
        self.working_dir = None
        if database is not None:
            self.db = database
            self.db_stats()

        if uuid is not None:
            self.uuid = uuid
            self.working_dir = os.path.join('D:/','LSC_PM_simulation_results', self.uuid)#changed by chong to fix my computer's problem
            self.graph_dir = os.path.join(self.working_dir, 'graphs')
            try_db_location = os.path.join(self.working_dir, "db.sqlite")
            if database is None and os.access(try_db_location, os.R_OK):
                self.db = PhotonDatabase.PhotonDatabase(dbfile=try_db_location, readonly=True)
            
        self.log = logging.getLogger('pvtrace.analysis')
        # Cached data
        self.uids = None
        self.count = None

        self.edges = ['left', 'near', 'far', 'right']
        self.apertures = ['top', 'bottom']
        self.faces = self.edges + self.apertures

    def add_db(self, database):
        self.db = database

    def db_stats(self):
        if self.uids is not None:
            return

        self.uids = {}
        self.count = {}

        # PHOTON GENERATED
        self.uids['generated'] = self.db.uids_generated_photons(max=True)
        # PHOTON KILLED
        self.uids['killed'] = self.db.killed()
        # TOTAL PHOTON SIMULATED
        self.uids['tot'] = diff(self.uids['generated'], self.uids['killed'])
        # PHOTON LOST
        self.uids['losses'] = self.db.uids_nonradiative_losses()
        # LUMINESCENT PHOTONS EDGES
        self.uids['luminescent_edges'] = []
        for surface in self.edges:
            self.uids['luminescent_'+surface] = self.db.uids_out_bound_on_surface(surface, luminescent=True)
            self.uids['luminescent_edges'] += self.uids['luminescent_'+surface]
        # LUMINESCENT PHOTONS APERTURES
        self.uids['luminescent_apertures'] = []
        for surface in self.apertures:
            self.uids['luminescent_' + surface] = self.db.uids_out_bound_on_surface(surface, luminescent=True)
            self.uids['luminescent_apertures'] += self.uids['luminescent_' + surface]
        # SOLAR PHOTONS (top/bottom)
        self.uids['solar_apertures'] = []
        for surface in self.apertures:
            self.uids['solar_' + surface] = self.db.uids_out_bound_on_surface(surface, solar=True)
            self.uids['solar_apertures'] += self.uids['solar_' + surface]

        # BACK SCATTER
        self.uids['bounds_back_scatter'] = self.db.uids_out_backscatter()

        # CELL & EXCITED ELECTRON
        self.uids['photovoltaic'] = self.db.uids_in_photovoltaic()
        self.uids['electron'] = self.db.uids_electron()

        # SOLAR PHOTONS (edges)
        self.uids['solar_edges'] = []
        for surface in self.edges:
            self.uids['solar_'+surface] = self.db.uids_out_bound_on_surface(surface, solar=True)
            self.uids['solar_edges'] += self.uids['solar_'+surface]

        # CHANNELS
        self.uids['luminescent_channel'] = self.db.uids_in_reactor_and_luminescent()
        self.uids['channels_tot'] = self.db.uids_in_reactor()
        self.uids['channels_direct'] = diff(self.uids['channels_tot'], self.uids['luminescent_channel'])

        # tubing only focus on uids
        self.uids['tubing'] = self.db.uids_in_tubing()


        # Calculate sum (for loop iterates only the keys of the dictionary)
        for key in self.uids:
            self.count[key] = len(self.uids[key])
        self.count['luminescent_faces'] = self.count['luminescent_edges'] + self.count['luminescent_apertures']
        self.count['solar_faces'] = self.count['solar_edges'] + self.count['solar_apertures']
        self.count['losses_total'] = self.count['losses'] + self.count['photovoltaic']

        # Controls
        difference = self.count['channels_tot'] - self.count['luminescent_channel']
        assert self.count['channels_direct'] == difference, "Difference of array failed"

        delta = abs(self.count['tot'] - (self.count['solar_faces'] + self.count['luminescent_faces'] +
                self.count['losses_total'] + self.count['channels_tot'] + self.count['bounds_back_scatter']))

        if delta == 0:
            self.log.info("[db_stats()] Results sanity check OK!")
        else:
            if (delta / self.count['tot']) < 0.001:
                self.log.warn("[db_stats()] Results FAILED sanity check!!!")
            else:
                raise ArithmeticError('Sum of photons per fate and generate do not match!'
                                      '(Delta: '+str(delta)+'/'+str(self.count['tot'])+' [Error > 0.1%!]')

    def percent(self, num_photons):
        """
        Return the percentage of num_photons with respect to thrown photons as 2 decimal digit string
        :param num_photons: number of photons to be divided by the total
        :rtype: string
        """
        # This needs "from __future__ import division"
        assert self.count['tot'] > 0, "Total photons are zero"
        return format((num_photons / self.count['tot']) * 100, '.2f') + ' % (' + str(num_photons).rjust(6, ' ') + ' )'

    def print_detailed(self):
        """
        Prints a detailed report on the fate of the photons stored in self.db

        :return:None
        """
        self.db_stats()

        self.log.debug('Print_detailed() called on DB with ' + str(self.count['generated']) + ' photons')

        self.log.info("Technical details:")
        self.log.info("\t Generated \t" + str(self.count['generated']))
        self.log.info("\t Killed \t" + str(self.count['killed']))
        self.log.info("\t Thrown \t" + str(self.count['tot']))

        self.log.info("Luminescent photons:")
        for surface in self.faces:
            self.log.info("\t" + surface + "\t" + self.percent(self.count['luminescent_' + surface]))

        self.log.info("Non radiative losses\t" + self.percent(self.count['losses']))
        self.log.info("Solar photons:")

        for surface in self.apertures:
            self.log.info("\t" + surface + "\t" + self.percent(self.count['solar_' + surface]))

        self.log.info("Reactor's channel photons:")
        self.log.info("Photons in channels (direct)\t" + self.percent(self.count['channels_direct']))
        self.log.info("Photons in channels (luminescent)\t" + self.percent(self.count['luminescent_channel']))
        self.log.info("Photons in channels (sum)\t" + self.percent(self.count['channels_tot']))

    def print_wavelength_channels(self, only_luminescent=True):
        """
        Prints the wavelengths of the photons absorbed by the channels.

        :param only_luminescent: Boolean, if true returns only the luminescent photons, if false also solar ones
        :return: csv string with headers
        """
        self.log.debug("Print_wavelength_channels called")
        self.db_stats()

        if only_luminescent:
            ret_str = " Photons in reactor (luminescent only). Wavelengths in nm"
            for photon in self.uids['luminescent_channel']:
                ret_str += " ".join(map(str, self.db.wavelength_for_uid(photon)))  # Clean output (for elaborations)
        else:
            ret_str = " Photons in reactor (all). Wavelengths in nm"
            for photon in self.uids['channels_tot']:
                ret_str += " ".join(map(str, self.db.wavelength_for_uid(photon)))  # Clean output (for elaborations)

        return ret_str

    def print_excel_header(self, additional=None, backscatter = False, photovoltaic = False):
        """
        Column header for print_excel()
        """
        if backscatter:
            r_text = "Generated, Killed, Total, Losses, Luminescent - Left, Luminescent - Near, Luminescent - Far, " \
                   "Luminescent - Right, Luminescent - Top, Luminescent - Bottom, Solar - Top, Solar - Bottom, Solar - edge," \
                   "Channels - Direct, Channels - Luminescent, BoundsLoss - backscatter"

        elif photovoltaic:
            r_text = "Generated, Killed, Total, Losses, Luminescent - Left, Luminescent - Near, Luminescent - Far, " \
                     "Luminescent - Right, Luminescent - Top, Luminescent - Bottom, Solar - Top, Solar - Bottom, Solar - edge," \
                     "Channels - Direct, Channels - Luminescent, photovoltaic - absorb, electron - excited"

        else:
            r_text = "Generated, Killed, Total, Losses, Luminescent - Left, Luminescent - Near," \
                     "Luminescent - Far, Luminescent - Right, Luminescent - Top, Luminescent - Bottom," \
                     "Solar - Top, Solar - Bottom, Solar - edge, Channels - Direct, Channels - Luminescent"
        self.log.info(r_text)
        return r_text

    def print_excel(self, additions=None, backscatter = False, photovoltaic = False):
        """
        Prints an easy to import report on the fate of the photons stored in self.db
        """
        self.db_stats()
        # todo: rewrite as list of keys and print them all from self.count

        if additions is None:
            return_text = ''
        else:
            return_text = str(additions) + ", "
        # GENERATED
        return_text += str(self.count['generated']) + ", "
        # KILLED
        return_text += str(self.count['killed']) + ", "
        # THROWN (GENERATED-KILLED)
        return_text += str(self.count['tot']) + ", "
        # NON RADIATIVE LOSSES
        return_text += str(self.count['losses']) + ", "

        edges = ['left', 'near', 'far', 'right']
        apertures = ['top', 'bottom']
        faces = edges + apertures

        # LUMINESCENT: left, near, far, right, top, bottom
        for surface in faces:
            return_text += str(self.count['luminescent_' + surface]) + ", "

        # SOLAR: top and bottom
        for surface in apertures:
            return_text += str(self.count['solar_' + surface]) + ", "

        return_text += str(self.count['solar_edges']) + ", "

        if backscatter:
            return_text += str(self.count['bounds_back_scatter'])+ ", "

        # CHANNELS (lumi, direct)
        return_text += str(self.count['channels_direct']) + ", "
        return_text += str(self.count['luminescent_channel']) + ", "
        if photovoltaic:

            return_text += str(self.count['photovoltaic']) + ", "
            return_text += str(self.count['electron'])

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
        return self.db.uids_for_pid(pid)

    def history_from_uid(self, uid=None):
        """
        Extract from the DB the trace of the given photon uid.
        If a list of uids is provided it's split into individual traces

        :param uid: list uid of photon to be investigated
        """
        
        # No uid
        if uid is None:
            return False
        
        # Single uid
        if isinstance(uid, int) or isinstance(uid, float):
            return self.history_from_pid(self.db.pid_from_uid(uid))
        
        # List of uids
        history = []
        pids = self.db.pid_from_uid(uid)
        for pid in pids:
            history.append(self.history_from_pid(pid))
        return history
    
    def describe_trajectory(self, uid_list=None):
        """
        Describe one or multiple uid-based photon trajectory
        
        :param uid_list: the list(s) of uids of the trajectory
        :return: None
        """
        if isinstance(uid_list[0], list) is False:
            self.log.info("describe_trajectory() uids provided: "+str(sorted(uid_list)))
            return self.describe_photon_path(uid_list)
        else:
            return_values = []
            for trajectory in uid_list:
                return_values.append(self.describe_photon_path(trajectory))
            return return_values
    
    def describe_photon_path(self, path, full_description=False):
        """
        Describe a photon trajectory
        
        :param path: uid-based photon trajectory
        :return:
        """
        trajectory = Trajectory.Trajectory()
        for step in path:
            position = self.db.value_for_table_column_uid(table='position', column=('x', 'y', 'z'), uid=step)
            direction = self.db.value_for_table_column_uid(table='direction', column=('x', 'y', 'z'), uid=step)
            polarization = self.db.value_for_table_column_uid(table='polarisation', column=('x', 'y', 'z'), uid=step)
            wavelength = self.db.value_for_table_column_uid(table='photon', column='wavelength', uid=step)
            state = self.db.value_for_table_column_uid(table='state',
                                                       column=('absorption_counter', 'intersection_counter', 'active',
                                                               'killed', 'source', 'emitter_material',
                                                               'absorber_material', 'container_obj', 'on_surface_obj',
                                                               'surface_id', 'ray_direction_bound', 'reaction'),
                                                       uid=step)
            self.log.debug("state is "+str(state))

            trajectory.add_step(position=position, direction=direction, polarization=polarization,
                                wavelength=wavelength, active=state[2], container=state[7], on_surface_object=state[8])
        return trajectory

    def create_graphs(self, prefix=''):
        """
        Generate a series of graphs on photons stored in self.db

        :param prefix:
        :return:
        """
        self.log.debug("Analysis.create_graphs() called with prefix=" + prefix)
        self.db_stats()

        if hasattr(self, 'uuid'):
            prefix = self.graph_dir
            try:
                os.stat(prefix)
            except OSError:
                os.mkdir(prefix)
        else:
            prefix = os.path.join(os.path.expanduser('~'), 'pvtrace_data')

        graphs = {
            'reactor-total': self.uids['channels_tot'],
            'reactor-luminescent': self.uids['luminescent_channel'],
            'lsc-edges': self.uids['luminescent_edges'],
            'lsc-apertures': self.uids['luminescent_apertures'],
            'lsc-reflected': self.uids['solar_top'],
            'lsc-transmitted': self.uids['solar_bottom'],
            'losses': self.uids['losses']}

        # noinspection PyCompatibility
        for plot, uid in six.iteritems(graphs):
            if len(uid) < 10:
                self.log.info('[' + plot + "] The database doesn't have enough photons to generate this graph!")
            else:
                wavelengths = self.db.original_wavelength_for_uid(uid)
                file_path = os.path.join(prefix, plot)
                self.save_histogram(data=wavelengths, filename=file_path)

        # return True
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
            data = self.get_bounces(photon_list=uids)
            xyplot(x=data[0], y=data[1], filename=os.path.join(prefix, 'bounces_all'))

    def calculate_photon_balance(self, detailed=False):
        """
        Calculate and export to file the photon balance of the simulation

        """
        self.log.debug("Analysis.calculate_photon_balance() called")
        self.db_stats()

        if detailed:
            fractions = ('generated', 'killed', 'tot', 'losses', 'luminescent_left', 'luminescent_near',
                         'luminescent_far', 'luminescent_right', 'luminescent_top', 'luminescent_bottom',
                         'solar_top', 'solar_bottom', 'channels_direct', 'luminescent_channel')
        else:
            fractions = ('generated', 'killed', 'tot', 'losses', 'luminescent_edges', 'luminescent_apertures',
                         'solar_top', 'solar_bottom', 'channels_direct', 'luminescent_channel')

        photon_balance = {}
        counter = 0
        for photon_fraction in fractions:
            self.log.info("Calculating "+photon_fraction)
            wavelength, photons = self.histogram_raw_data(
                data=self.db.original_wavelength_for_uid(self.uids[photon_fraction]), wavelength_range=(350, 700))
            if counter == 0:
                wl = ['{:.0f}'.format(x) for x in wavelength]
                # print(wl)
                photon_balance[0] = ['wavelength', ] + wl
                counter += 1
            photon_balance[counter] = (photon_fraction,) + photons
            counter += 1

        return photon_balance

    def save_photon_balance(self, photon_balance, file_name='photon_balance'):
        """
        Save a photon balance (result of self.calculate_photon_balance()) into a csv file

        :param photon_balance: photon balance data
        :param file_name: filename for csv export
        """
        self.log.debug("Analysis.save_photon_balance() called with filename=" + file_name)

        if hasattr(self, 'uuid'):
            prefix = self.graph_dir
            try:
                os.stat(prefix)
            except OSError:
                os.mkdir(prefix)
        else:
            prefix = os.path.join(os.path.expanduser('~'), 'pvtrace_data')

        file_path = os.path.join(prefix, file_name+'.tsv')
        with open(file_path, 'wb') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter="\t")

            for key, value in photon_balance.items():
                writer.writerow(value)

    def save_histogram(self, data, filename, wavelength_range=(350, 700)):
        """
        Save the cumulative distribution of photons in the wavelength range specified to filename as csv file

        :param data: List with photons' wavelengths
        :param filename: Filename for the exported file. Will be saved in home/pvtrace_export/filename (+.csv appended)
        :param wavelength_range : range of wavelength to be plotted (X axis)
        """
        self.log.debug("Saving histograpm data for " + filename)

        export_dir = os.path.join(self.working_dir, 'graphs')
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        export_location = os.path.join(export_dir, filename + '.csv')

        a, b = self.histogram_raw_data(data=data, wavelength_range=wavelength_range)
        data_array = zip(a, b)
        np.savetxt(fname=export_location, X=data_array, delimiter=', ', newline="\n", fmt='%9.0f',
                   header="wavelength, count")

    @staticmethod
    def histogram_raw_data(data, wavelength_range=(350, 700)):
        """
        Transform the wavelength range in binned data

        :param data: List with photons' wavelengths
        :param wavelength_range : range of wavelength to be plotted (X axis)
        """
        histo = np.histogram(data, bins=np.arange(start=math.floor(wavelength_range[0]),
                                                  stop=math.ceil(wavelength_range[1]) + 1))
        data = zip(*histo)
        # Reverse order to have wavelength first
        count, wavelength = zip(*data)
        return wavelength, count

    def save_db(self, location=None):
        self.db.dump_to_file(location)


# fixme: move this to Spectrum
def histogram(data, filename, wavelength_range=(350, 700)):
    """
    Create an histogram with the cumulative frequency of photons at different wavelength

    :param data: List with photons' wavelengths
    :param filename: Filename for the exported file. Will be saved in the working dirhome/pvtrace_export/filenam (+.png appended)
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


# List difference
def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]
