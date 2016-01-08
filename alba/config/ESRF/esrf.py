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

"""
configuration file for an example of how to specify system-wide defaults for VaccaGUI 

This configuration file determines the default, permanent, pre-defined
options for the GUI; modify them to match your default gui options.

Every CONFIG file loaded by vaccagui will override those options redefined on it; 
use default.py for your common options and whatever.py for your in-place customization.
"""

print '>'*20+' Loading %s'%__name__

from vacca.utils import DEFAULT_PATH

WDIR = DEFAULT_PATH
DOMAIN = 'ID03'
COMPOSER = 'ID03/VC/ALL'
JDRAW_FILE = WDIR+'ESRF/id03.jdw'
GRID = {
    'model': 'ID03/V-(PEN|VARIP)/*/Pressure',
    'row_labels':'VcGauges(mbar):V-PEN, IonPumps(mbar):VARIP',
    'column_labels':'ALL:*',
    'delayed':False,
    }
import fandango
GAUGES = fandango.get_matching_attributes('ID03/V-PEN/*/Pressure')

#Loading APPS from config doesnt work!!!

#For ExternalApp/VaccaActions use:
# {'$VarName':{'name':'$AppName','classname':'VaccaAction','model':['$Test','$/path/to/icon.png','$launcher']}}
#xrga = AppletDescription('RGA',classname = 'VaccaAction',model=['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01'])
EXTRA_APPS = {
    'xrga':{'name':'RGA','classname':'vacca.panel.VaccaAction','model':['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01']}
    }