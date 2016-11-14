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
from __future__ import division
import numpy as np
from pvtrace.external import transformations
from pvtrace.external import pov
from pvtrace.external import quickhull
from pvtrace.external import mathutils

from pvtrace.Materials import *
from pvtrace.Devices import *
from pvtrace.Geometry import *
from pvtrace.ConstructiveGeometry import *
from pvtrace.LightSources import *
from pvtrace.Visualise import *
from pvtrace.Trace import *
from pvtrace.Interpolation import *

import os
import sys
import logging

logger = logging.getLogger('pvtrace')
logger.info('pvtrace pre-flight checks...')

# Module constants -- location of the data folder
logger.info('System Path: '+str(sys.path))
pvtrace_containing_directory = False
for path in sys.path:
    if path.find('pvtrace') != -1:
        pvtrace_containing_directory = path
        break

if pvtrace_containing_directory is not False:
    while pvtrace_containing_directory.find('pvtrace') != -1:
        pvtrace_containing_directory = os.path.abspath(os.path.join(pvtrace_containing_directory, '..'))
else:
    pvtrace_containing_directory = os.path.expanduser('~')

PVTDATA = os.path.join(pvtrace_containing_directory, 'pvtrace', 'data')
logger.info('PVTDATA set to '+PVTDATA)
