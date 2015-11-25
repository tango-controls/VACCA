#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
###########################################################################

print '#'*80
print 'vacca.__init__'

__doc__ = """
-------------------------------------------------------------
VACCA, the Viewer and Commander Control Application for TANGO
-------------------------------------------------------------

The *vacca* library is divided in different submodules:

 * config : the vacca MAIN file, a config setup to highly customize TaurusGUI instances
 * doc : helper methods to build documentation
 * setup :  script to download and install vacca and its dependencies from sourceforge
 * utils : miscellaneous methods to manage folders, config files, look&feel 

Several other modules contain the widget catalog: 

 * alarms
 * grid : grid-like synoptics
 * panel : device/attribute panels and forms
 * plot : trends and plots
 * properties : property editor widget
 * synoptics
 
"""

from vacca.doc import get_autodoc
from vacca.panel import *
from vacca.tree import *
from vacca.utils import *
from vacca.properties import *
from vacca.grid import *
from vacca.alarms import *

## THIS DIDNT WORKED!!
#print('Autogenerating VACCA docs')
#import panel,tree,utils,properties,grid,vaccaPanic,doc
#for m in panel,tree,utils,properties,grid,vaccaPanic:
    #print m.__name__
    #if not m.__doc__:
        #m.__doc__ = "\n%s\n%s\n\n" % (m.__name__,'='*len(m.__name__))
    #if ".. auto" not in m.__doc__:
        #m.__doc__+=doc.get_function_docs(m.__name__,vars(m))
        #m.__doc__+=doc.get_class_docs(m.__name__,vars(m))

__doc__+="\nextended"

#try:
 #from config import *
#except Exception,e:
 #print 'Unable to import vacca.config: %s'%str(e)
