from __future__ import division
import numpy as np
import sqlite3 as sql
import inspect
import types
import os
import pvtrace

# The database schema lives inside the pvtrace module directory
DB_SCHEMA = os.path.join(os.path.dirname(pvtrace.__file__), "dbschema.sql")


def counted(fn):
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return fn(*args, **kwargs)

    wrapper.called = 0
    wrapper.__name__ = fn.__name__
    return wrapper


def itemise(array):
    """Extracts redundant nested arrays from a parent array e.g. [(1,), (2,), (3,), (4,)] becomes (1,2,3,4)."""
    new = []
    is_values = None
    is_points = None
    for item in array:
        
        if isinstance(item, types.ListType) or isinstance(item, types.TupleType):
            
            if len(item) == 1:
                # The data is comprised of single values
                new.append(item[0])
                is_values = True
            
            if len(item) == 3:
                # The data is comprised of cartesian points
                is_points = True
                new.append(item)
            
            if is_values == is_points:
                raise "All elements must of the array must be singleton arrays (i.e. single element arrays)", ValueError
    
    return new


class PhotonDatabase(object):
    """
    An object the wraps a mysql database.
    """

    def __init__(self, dbfile=None):
        """
        Create the database and loads the schema into it.

        :param dbfile: Filename for the database. If None then a RAM DB will be used (way faster!)
        """
        super(PhotonDatabase, self).__init__()

        self.uid = 0
        self.split_size = 20000

        if dbfile is not None:
            # There is a defa
            self.file = dbfile
            
            # Delete this dbfile and start again
            if os.path.exists(self.file):
                if os.path.split(self.file)[1] == "pvtracedb.sql":
                    os.remove(self.file)
                else:
                    raise ValueError("A database already exist at '%s', please rename your database" % self.file)
            
            # print "Attempting to creating database dbfile...", self.file
            try:
                file(self.file, 'w').close()
            except:
                raise IOError("Could not create file, %s" % self.file)
            
            self.connection = sql.connect(self.file)
        else:
            self.file = None
            self.connection = sql.connect(":memory:")

        self.cursor = self.connection.cursor()

        # Faster DB on disk without journaling
        if self.file is not None:
            self.cursor.execute("PRAGMA synchronous = OFF")
            self.cursor.execute("PRAGMA journal_mode = OFF")

        try:
            # print "Attempting to loading schema into database from dbfile ... ", DB_SCHEMA
            dbfile = open(os.path.abspath(DB_SCHEMA), "r")
            for line in dbfile:
                self.cursor.execute(line)
        except Exception as inst:
            print "Could not load DB schema file. (", DB_SCHEMA, ")"
            print type(inst)
            print inst
            exit(1)

    def load(self, dbfile):
        """Loads and exisiting photon database into memory from a dbfile path."""
        self.connection = sql.connect(dbfile)
        self.cursor = self.connection.cursor()

    def log(self, photon, surface_normal=None, on_surface_obj=None, surface_id=None, ray_direction_bound=None,
            emitter_material=None, absorber_material=None):
        """
        Adds a new row to the database. NB Every time this function is called the uid of the photon is incremented.
        """
        values = (self.uid, photon.id, float(photon.wavelength))
        # import pdb; pdb.set_trace()
        self.cursor.execute('INSERT INTO photon VALUES (?, ?, ?)', values)
        
        values = (float(photon.position[0]), float(photon.position[1]), float(photon.position[2]), self.uid)
        # print values
        # for v in values:
        #    print type(v)
        self.cursor.execute('INSERT INTO position VALUES (?, ?, ?, ?)', values)
        
        values = (float(photon.direction[0]), float(photon.direction[1]), float(photon.direction[2]), self.uid)
        self.cursor.execute('INSERT INTO direction VALUES (?, ?, ?, ?)', values)
        
        try:
            values = (
            float(photon.polarisation[0]), float(photon.polarisation[1]), float(photon.polarisation[2]), self.uid)
            self.cursor.execute('INSERT INTO polarisation VALUES (?, ?, ?, ?)', values)
        except:
            pass
        
        if surface_normal is not None:
            values = (float(surface_normal[0]), float(surface_normal[1]), float(surface_normal[2]), self.uid)
            self.cursor.execute('INSERT INTO surface_normal VALUES (?, ?, ?, ?)', values)
        
        # Filter parameters that can be None
        if photon.container is None:
            container_obj = None
        else:
            container_obj = str(photon.container.name)
        
        if photon.on_surface_object is None:
            on_surface_obj = None
        else:
            on_surface_obj = photon.on_surface_object.name
        
        values = (photon.absorption_counter, photon.intersection_counter, photon.active, photon.killed, photon.source,
                  emitter_material, absorber_material, container_obj, str(on_surface_obj), str(surface_id),
                  str(ray_direction_bound), photon.reaction, self.uid)
        self.cursor.execute('INSERT INTO state VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', values)
        
        # the last line of this method update the unique photon ID (i.e. the row number)
        self.uid += 1
        
        # Every 50 times write data to dbfile
        if self.uid % 50 == 0:
            self.connection.commit()

    def dump_to_file(self, location=None):
        """
        Saves to file the current DB to a given location. Useful for in-memory DBs

        NOTE: it doesn't update self.connection with the new location, so the old db will still be used for further
         query (intended behaviour since, if it's :memory:, is presumably faster

        :param location: complete URL (path+filename) to save the db to
        :return:
        """
        # Seems impossible to instal sqlitebck on Windows, linking fails with Visual C++ for Python 2.7 even when
        # sqlite head file and *.lib are provided.
        # import apsw
        import sqlitebck
        if location is None:
            filename = os.path.join(os.path.expanduser('~'), 'pvtracedb.sql')
        else:
            filename = location

        file_connection = sql.connect(filename)
        sqlitebck.copy(self.connection, file_connection)
        print "\r DB copy saved as ", filename

    def add_db_file(self, filename=None,
                    tables=("state", "direction", "polarisation", "position", "surface_normal", "photon")):
        """
        Adds the data in the give filename db to the current DB (only the tables in tables)

        Used by split_db option to re-merge dumped dbs at the end of simulation

        :param filename: Filename of the db to be added
        :param tables: Tables to be added
        """
        self.cursor.execute("ATTACH DATABASE ? AS  toMerge", [filename])
        for table in tables:
            self.cursor.execute("INSERT INTO " + table + " SELECT * FROM toMerge." + table)
        self.cursor.execute("DETACH DATABASE toMerge")

    def empty(self):
        """
        Empties DB
        """
        self.cursor.execute("DELETE FROM state")
        self.cursor.execute("DELETE FROM direction")
        self.cursor.execute("DELETE FROM polarisation")
        self.cursor.execute("DELETE FROM position")
        self.cursor.execute("DELETE FROM surface_normal")
        self.cursor.execute("DELETE FROM photon")
        self.connection.commit()

    def __del__(self):
        self.cursor.close()
    
    def endpoint_uids(self):
        return itemise(self.cursor.execute('SELECT MAX(uid) FROM photon GROUP BY pid;').fetchall())
    
    def endpoint_uids_for_object(self, obj):
        return itemise(self.cursor.execute("SELECT MAX(uid) FROM photon GROUP BY pid INTERSECT SELECT uid FROM state"
                                           "WHERE on_surface_obj=? OR container_obj=?", (obj, obj)).fetchall())
    
    def endpoint_uids_for_surface(self, surface):
        return itemise(self.cursor.execute("SELECT MAX(uid) FROM photon GROUP BY pid INTERSECT SELECT uid"
                                           "FROM state WHERE surface_id=?;", (surface,)).fetchall())
    
    def endpoint_uids_for_object_and_surface(self, obj, surface):
        return itemise(self.cursor.execute("SELECT MAX(uid) FROM photon GROUP BY pid INTERSECT SELECT uid FROM state WHERE on_surface_obj=? AND surface_id=?;",
            (obj, surface)).fetchall())
    
    def endpoint_uids_outbound_for_object_and_surface(self, obj, surface, luminescent=None, solar=None):
        """
        For a surface_id will return all endpoint uid on an out bound direction.
        If keyword luminescent=True, then only luminescent photons will be returned.
        If solar=True, the only solar photons will be returned.
        If both are True then both types are returned i.e. the default behaviour.
        Setting the keywords to any other value is ignored.
        """
        if luminescent == solar and luminescent is None:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN'
                '(SELECT uid FROM state WHERE ray_direction_bound = "Out" AND on_surface_obj=? AND surface_id=?'
                'GROUP BY uid);',(obj, surface)).fetchall())
        elif luminescent:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN'
                '(SELECT uid FROM state WHERE'
                'ray_direction_bound = "Out" AND on_surface_obj=? AND surface_id=? AND absorption_counter > 0'
                'GROUP BY uid);', (obj, surface)).fetchall())
        elif solar:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN'
                '(SELECT uid FROM state WHERE'
                'ray_direction_bound = "Out" AND on_surface_obj=? AND surface_id=? AND absorption_counter = 0'
                'GROUP BY uid);', (obj, surface)).fetchall())
        else:
            print "Cannot return any uids for this question." \
                  "Are you using the function uids_out_bound_on_surface correctly?"
            return []

    def endpoint_uids_for_nonradiative_loss(self):
        return itemise(self.cursor.execute(
            "SELECT uid FROM state WHERE surface_id = 'None' AND absorption_counter > 0 AND killed = 0"
            "GROUP BY uid HAVING uid IN (SELECT MAX(uid) FROM photon group BY pid)").fetchall())
    
    def endpoint_uids_for_nonradiative_loss_in_object(self, obj):
        return itemise(self.cursor.execute(
            "SELECT uid FROM state WHERE"
            "container_obj=? AND surface_id = 'None' AND absorption_counter > 0 AND killed = 0"
            "GROUP BY uid HAVING uid IN (SELECT MAX(uid) FROM photon group BY pid)", (obj,)).fetchall())
    
    def killed(self):
        """Returns the uid of killed photons (one that took too many steps to complete)."""
        return self.cursor.execute('SELECT uid FROM state WHERE killed = 1').fetchall()

    def missed(self):
        """Returns the uid of photons that did not hit any scene objects"""
        pass
    
    def objects_with_records(self):
        """Returns a list of which scene object have been hit by rays."""
        objects_keys = self.cursor.execute(
            'SELECT DISTINCT(container_obj) FROM state GROUP BY container_obj;').fetchall()
        objects_keys = itemise(objects_keys)
        filtered_keys = []
        # When rays are first created they are logged but they don't have a container_obj (it is assigned later).
        # Here we are remove 'None' from the hit object list, and also converting unicode strings to strings.
        for key in objects_keys:
            if key != 'None' or key != u'None' or key is not None:
                filtered_keys.append(str(key))
        return filtered_keys

    def surfaces_with_records(self):
        """Returns surfaces that have been hit by a ray for all exiting objects.
        """
        keys = self.cursor.execute(
            'SELECT DISTINCT surface_id FROM state WHERE uid IN (SELECT uid FROM surface_normal'
            'WHERE uid IN (SELECT MAX(uid) FROM photon GROUP BY pid));').fetchall()
        keys = itemise(keys)
        filtered_keys = []
        # Surface record will often be None because event occur away from surface (i.e. absorption emission)
        # Here we are remove 'None' from the list, and also converting unicode strings to strings.
        for key in keys:
            if key != 'None' or key != u'None':
                filtered_keys.append(str(key))
        return filtered_keys
    
    def surfaces_with_records_for_object(self, obj):
        """Returns a list of surface to 'object' that have been hit by a ray."""
        keys = itemise(self.cursor.execute(
            'SELECT DISTINCT surface_id FROM state WHERE uid IN (SELECT uid FROM surface_normal'
            'WHERE uid IN (SELECT MAX(uid) FROM photon GROUP BY pid))'
            'INTERSECT SELECT DISTINCT surface_id FROM state WHERE container_obj=?;', (obj,)).fetchall())

    def surface_normal_for_surface(self, surface_id, position_on_surface=None):
        """
        Returns a surface normal (vector) for a specified surface_id.
        If the surface is curved, you will need to specify the point on the surface.
        """
        return self.cursor.execute(
            'SELECT x,y,z FROM surface_normal WHERE uid = (SELECT MIN(uid) FROM state WHERE surface_id = ?)',
            (surface_id,)).fetchall()[0]

    def uids_out_bound_on_surface(self, surface_id, luminescent=None, solar=None):
        """
        For a surface_id will return all uid on an out bound direction. If keyword luminescent=True,
        then only luminescent photons will be returned. If solar=True, the only solar photons will be 
        returned. If both are True then both types are returned i.e. the default behaviour. Setting the keywords to any other value is ignored."""
        if luminescent == solar:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN (SELECT uid FROM state WHERE ray_direction_bound = "Out" AND surface_id=? GROUP BY uid);',
                (surface_id,)).fetchall())
        elif luminescent:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN (SELECT uid FROM state WHERE ray_direction_bound = "Out" AND surface_id=? AND absorption_counter > 0 GROUP BY uid);',
                (surface_id,)).fetchall())
        elif solar:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN (SELECT uid FROM state WHERE ray_direction_bound = "Out" AND surface_id=? AND absorption_counter = 0 GROUP BY uid);',
                (surface_id,)).fetchall())
        else:
            print "Cannot return any uids for this question. Are you using the function uids_out_bound_on_surface correctly?"
            return []

    def uids_in_bound_on_surface(self, surface_id, luminescent=None, solar=None):
        """
        For a surface_id will return all uid on an in bound direction.

        If keyword luminescent=True, then only luminescent photons will be returned.
        If solar=True, the only solar photons will be returned.
        If both are True then both types are returned i.e. the default behaviour.
        Setting the keywords to any other value is ignored.
        """
        if luminescent == solar:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN (SELECT uid FROM state WHERE ray_direction_bound = "In" AND surface_id=? GROUP BY uid);',
                (surface_id,)).fetchall())
        elif luminescent:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN (SELECT uid FROM state WHERE ray_direction_bound = "In" AND surface_id=? AND absorption_counter > 0 GROUP BY uid);',
                (surface_id,)).fetchall())
        elif solar:
            return itemise(self.cursor.execute(
                'SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN (SELECT uid FROM state WHERE ray_direction_bound = "In" AND surface_id=? AND absorption_counter = 0 GROUP BY uid);',
                (surface_id,)).fetchall())
        else:
            print "Cannot return any uids for this question. Are you using the function uids_in_bound_on_surface correctly?"
            return []
    
    def uids_in_reactor(self):
        """Returns photons in reactor"""
        return itemise(self.cursor.execute(
            "SELECT MAX(uid) FROM photon GROUP BY pid INTERSECT SELECT uid FROM state WHERE reaction = 1"))
    
    def uids_in_reactor_and_luminescent(self):
        """Returns photons in reactor and luminescent One absorption is.the reaction mixture, so >1"""
        return itemise(self.cursor.execute(
            "SELECT MAX(uid) FROM photon GROUP BY pid INTERSECT SELECT uid FROM state WHERE reaction = 1 AND absorption_counter > 1"))
    
    def uids_luminescent(self):
        """Returns luminescent photons"""
        return itemise(self.cursor.execute(
            "SELECT MAX(uid) FROM photon GROUP BY pid INTERSECT SELECT uid FROM state WHERE absorption_counter > 1"))

    def uids_first_intersection(self):
        """Returns the unique identifier of the first intersection for all photons"""
        return self.cursor.execute('SELECT uid FROM state WHERE intersection_counter = 1;').fetchall()
    
    def uids_generated_photons(self):
        return self.cursor.execute('SELECT MIN(uid) FROM photon GROUP BY pid;').fetchall()
    
    def pid_from_uid(self, uid):
        return self.cursor.execute('SELECT pid FROM photon WHERE uid=?', (uid,)).fetchall()

    def uids_for_pid(self, pid):
        return itemise(self.cursor.execute('SELECT uid FROM photon WHERE pid=?', (pid,)))
    
    def bounces_for_pid(self, pid):
        last_uid_for_pid = max(self.uids_for_pid(pid))
        return itemise(self.cursor.execute('SELECT absorption_counter FROM state WHERE uid=?', (last_uid_for_pid,)))

    def bounces_for_uid(self, uid):
        return itemise(self.cursor.execute('SELECT absorption_counter FROM state WHERE uid=?', (uid,)))

    def uids_nonradiative_losses(self):
        return itemise(self.cursor.execute(
            "SELECT uid FROM state WHERE reaction = 0 AND surface_id = 'None' AND absorption_counter > 0 AND killed = 0 GROUP BY uid HAVING uid IN (SELECT MAX(uid) FROM photon group BY pid)").fetchall())
    
    def value_for_table_column_uid(self, table, column, uid):
        """Returns values from the database index my table, column and row, where the row is uniquely defined using the photon uid. 
        Column can also be array-like so multiple columns can be specified provided they come from the same table."""
        if type(column) is types.StringType or types.UnicodeType:
            return self.cursor.execute("SELECT ? FROM ? WHERE uid = ?", (column, table, uid)).fetchall()
        elif type(column) is types.ListType or types.TupleType:
            col_headers = ""
            for header in column:
                col_header += header
                if header is not column[-1]:
                    col_header += ', '
            return self.cursor.execute("SELECT (?) FROM ? WHERE uid = ?", (col_headers, table, uid)).fetchall()
        else:
            print "Cannot return any uids for this question. Are you using the function value_for_table_column_uid correctly?"
            return []

    def directionForUid(self, uid):
        if type(uid) == types.IntType or type(uid) == types.FloatType:
            return np.array(self.cursor.execute("SELECT x,y,z FROM direction WHERE uid = ?", (uid,)).fetchall()[0])
        elif type(uid) == types.ListType or type(uid) == types.TupleType:
            # This has a variable number of items so ignoring the secure way to do this... me bad
            items = str(uid)[1:-1]
            cmd = "SELECT x,y,z FROM direction WHERE uid IN (%s)" % (items,)
            return self.cursor.execute(cmd).fetchall()
    
    def polarisationForUid(self, uid):
        if type(uid) == types.IntType or type(uid) == types.FloatType:
            return np.array(self.cursor.execute("SELECT x,y,z FROM polarisation WHERE uid = ?", (uid,)).fetchall()[0])
        elif type(uid) == types.ListType or type(uid) == types.TupleType:
            items = str(uid)[1:-1]
            cmd = "SELECT x,y,z FROM polarisation WHERE uid IN (%s)" % (items,)
            return self.cursor.execute(cmd).fetchall()
    
    def positionForUid(self, uid):
        if type(uid) == types.IntType or type(uid) == types.FloatType:
            return np.array(self.cursor.execute("SELECT x,y,z FROM position WHERE uid = ?", (uid,)).fetchall()[0])
        elif type(uid) == types.ListType or type(uid) == types.TupleType:
            items = str(uid)[1:-1]
            cmd = "SELECT x,y,z FROM position WHERE uid IN (%s)" % items
            return self.cursor.execute(cmd).fetchall()

    def wavelengthForUid(self, uid):
        # import pdb; pdb.set_trace()
        if type(uid) == types.IntType or type(uid) == types.FloatType:
            return np.array(self.cursor.execute("SELECT wavelength FROM photon WHERE uid = ?", (uid,)).fetchall()[0])
        elif type(uid) == types.ListType or type(uid) == types.TupleType:
            items = str(uid)[1:-1]
            cmd = "SELECT wavelength FROM photon WHERE uid IN (%s)" % (items,)
            values = itemise(self.cursor.execute(cmd).fetchall())
            return values


if __name__ == "__main__":
    import PhotonDatabase
    import os
    import numpy as np
    import pylab
    
    # DRIVE exists only on Windows, using user data folder is more interoperable (Linux here!) [D.]
    # drive = os.path.splitdrive(os.path.expanduser("~"))[0]
    drive = os.path.expanduser("~")
    database_file = os.path.join(drive, "tmp", "pvtracedb.sql")
    
    if not os.path.exists(os.path.split(database_file)[0]):
        os.makedirs(os.path.split(database_file)[0])
    db = PhotonDatabase.PhotonDatabase()
    db.load(database_file)
    
    uid = db.uids_nonradiative_losses()
    if len(uid) == 0:
        print 'No photons lost! :)'
        print type(db)
        print db.objects_with_records()
    else:
        print uid
        print db.wavelengthForUid(uid)
        print ""
        print db.positionForUid(uid)
        print ""
        print db.directionForUid(uid)
        print ""
        print db.polarisationForUid(uid)
        
        print "Plotting Test"
        data = db.wavelengthForUid(uid)
        hist = np.histogram(data, bins=np.linspace(300, 800, num=100))
        pylab.hist(data, bins=np.linspace(300, 800, num=100), histtype='stepfilled')
        pylab.savefig(os.path.join(drive, "tmp", "plot-test.pdf"))
        pylab.clf()
    
    print "Plotting reactor..."
    uid = db.uids_in_reactor()
    # print "Photons in channels array is: ",uid
    data = db.wavelengthForUid(uid)
    hist = np.histogram(data, bins=np.linspace(300, 800, num=100))
    pylab.hist(data, 100, histtype='stepfilled')
    pylab.savefig(os.path.join(drive, "tmp", "plot-reactor.png"))
    pylab.clf()
    
    print "Plotting reactor luminescent..."
    uid = db.uids_in_reactor_and_luminescent()
    # print "Photons in channels array is: ",uid
    data = db.wavelengthForUid(uid)
    hist = np.histogram(data, bins=np.linspace(300, 800, num=100))
    pylab.hist(data, 100, histtype='stepfilled')
    pylab.savefig(os.path.join(drive, "tmp", "plot-reactor-luminescent.png"))
    pylab.clf()
    
    print(data)
    
    '''print "Plotting edge"
    uid = db.uids_out_bound_on_surface('left', luminescent=True) + db.uids_out_bound_on_surface('right', luminescent=True) + db.uids_out_bound_on_surface('near', luminescent=True) + db.uids_out_bound_on_surface('far', luminescent=True)
    print uid
    data = db.wavelengthForUid(uid)
    hist = np.histogram(data, bins=np.linspace(300,800,num=100))
    pylab.hist(data, 100, histtype='stepfilled')
    pylab.savefig(os.path.join(drive,"tmp","plot-edge.pdf"))
    pylab.clf()
    
    print "Plotting polar"
    for id in ['left','right', 'near', 'far']:
        data = []
        norm = db.surface_normal_for_surface(id)
        print "Surface", id, "Normal", norm
        uids = db.uids_out_bound_on_surface(id, luminescent=True)
        
        for item in uids:
            k = db.directionForUid(item)
            rads = pvtrace.angle(norm, k)
            deg = np.degrees(rads)
            data.append(deg)
    
    bins = np.linspace(0,360,num=100)
    hist = np.histogram(data, bins=bins)
    pylab.hist(data, 100, histtype='stepfilled')
    pylab.savefig(os.path.join(drive,"tmp",'plot-polar.pdf'))
    pylab.clf()
    
    print "Plotting escape"
    uid = db.uids_out_bound_on_surface('top', luminescent=True) + db.uids_out_bound_on_surface('bottom', luminescent=True)
    print uid
    data = db.wavelengthForUid(uid)
    hist, bin_edges = np.histogram(data, bins=np.linspace(300,800,num=10))
    pylab.hist(data, len(bin_edges), histtype='stepfilled')
    pylab.savefig(os.path.join(drive,"tmp",'plot-escape.pdf'))
    pylab.clf()
    
    print "Plotting reflected"
    uid = db.uids_out_bound_on_surface('bottom', solar=True)
    data = db.wavelengthForUid(uid)
    hist, bin_edges = np.histogram(data, bins=np.linspace(300,800,num=10))
    pylab.hist(data, len(bin_edges), histtype='stepfilled')
    pylab.savefig(os.path.join(drive,"tmp",'plot-reflected.pdf'))
    pylab.clf()
    
    uid = db.uids_out_bound_on_surface('top', solar=True)
    data = db.wavelengthForUid(uid)
    hist, bin_edges = np.histogram(data, bins=np.linspace(300,800,num=10))
    pylab.hist(data, len(bin_edges), histtype='stepfilled')
    pylab.savefig(os.path.join(drive,"tmp",'plot-transmitted.pdf'))
    pylab.clf()
    '''
