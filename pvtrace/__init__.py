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

from Materials import *
from Devices import *
from Geometry import *
from ConstructiveGeometry import *
from LightSources import *
from Visualise import *
from Trace import *
from Interpolation import *

import os
import sys

print("pvtrace pre-flight checks...")

# Module constants -- location of the data folder
# print(sys.path)
for path in sys.path:
    if path.find('pvtrace') != -1:
        pvtrace_containing_directory = path
        break
while pvtrace_containing_directory.find('pvtrace') != -1:
    pvtrace_containing_directory = os.path.abspath(os.path.join(pvtrace_containing_directory, '..'))

PVTDATA = os.path.join(pvtrace_containing_directory, 'pvtrace', 'data')

print("Pvtrace data directory:")
print(PVTDATA)
