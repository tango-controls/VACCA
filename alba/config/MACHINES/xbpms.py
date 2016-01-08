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

import fandango,imp

#The device that will be shown by default when loading the application
COMPOSER = DEVICE = 'sr/main/machinestatus'

print '>'*20+' Loading config for xbpms'

from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath
WDIR = WORKING_DIR

##NOTE: THIS DOESN'T SEEM TO WORK!
EXTRA_APPS = {
    'xtrend':{'name':'NewTrend','classname':'vacca.panel.VaccaAction','model':['Trend',wdir('image/icons/Mambo-icon.png')]+'taurustrend -a'.split()},
    }
    
EXTRA_DEVICES = fandango.get_matching_devices('fe*(xbpm|locum|alarm|adc)*')+['sr/main/machinestatus']

GAUGES = fandango.get_matching_attributes('fe*/di/xbpmlocum*/(x|y)pos')
    
JDRAW_FILE = '' #wdir('%s/%s.jdw'%(BL,BL))
print 'JDRAW_FILE: %s'%JDRAW_FILE

GRID = {
        'column_labels': ','.join('FE%02d'%i for i in (2,4,9,11,13,22,24,29)),
        'delayed': False,
        'frames': False,
        'model': 'fe*/di/xbpmlocum*/(state|x|y|I)*',
        'row_labels': 'State,1/X,1/Y,1/I'
    }

EXTRA_PANELS = []
EXTRA_PANELS.append(('Form','TaurusForm',''))
EXTRA_PANELS.append(('Props','TaurusPropTable','',{'SelectedInstrument':'setTable'},{}))
#EXTRA_PANELS.append(('PANIC','panic.gui.AlarmGUI','--'))
try:
    from PyTangoArchiving.widget.browser import ArchivingBrowser
    w = 'PyTangoArchiving.widget.browser.ArchivingBrowser'
except:
    from PyTangoArchiving.widget.ArchivingBrowser import ModelSearchWidget
    w = 'PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget'
EXTRA_PANELS.append(('Finder',w,''))

#NOT USED, HAVE A LOOK TO filters.AttributeFilters INSTEAD
def ATTR_FILTER(attr_name):
    attr_name = attr_name.lower()
    if attr_name.endswith('/status'):
        return False
    elif '/all/' in attr_name and any(s in attr_name for s in 
            'axxis,devstates,deviceslist,positions'.split(',')):
        return False
    elif 'vgct' in attr_name:
        if not fandango.matchCl('p[0-9]',attr_name) or 'not used' in attr_name: 
            return False
    return True
