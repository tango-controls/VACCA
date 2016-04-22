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
DEVICE = ''#sys/tg_test/1'
DOMAIN = 'LAB' #ID03'
COMPOSER = '' #ID03/VC/ALL'
JDRAW_FILE = '' #WDIR+'ESRF/id03.jdw'
GRID = {
    #'model': 'ID03/V-(PEN|VARIP)/*/Pressure',
    #'row_labels':'VcGauges(mbar):V-PEN, IonPumps(mbar):VARIP',
    'model': 'LAB/VC/*/P[0-9]',
    'row_labels':'VcGauges(mbar):(VGCT|MKS|CCG), IonPumps(mbar):(IPCT|DUAL)',
    'column_labels':'ALL:*',
    'delayed':False,
    }
import fandango
GAUGES = fandango.get_matching_attributes('lab/vc/vgct*/p[0-9]')#'ID03/V-PEN/*/Pressure')
EXTRA_DEVICES = ([d for d in fandango.get_matching_devices('lab/*/*') 
    if fandango.check_device(d) and not fandango.searchCl('(serial|mbus)',d)] +
    fandango.get_matching_devices('test/*/*'))

EXTRA_PANELS = []
EXTRA_PANELS.append(('PANIC','panic.gui.AlarmGUI','--'))
EXTRA_PANELS.append(('Form','TaurusForm',''))
try:
    from PyTangoArchiving.widget.browser import ArchivingBrowser
    w = 'PyTangoArchiving.widget.browser.ArchivingBrowser'
except:
    from PyTangoArchiving.widget.ArchivingBrowser import ModelSearchWidget
    w = 'PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget'
EXTRA_PANELS.append(('Finder',w,''))

EXTRA_WIDGETS = [
('panic.gui.AlarmGUI',WDIR+'image/icons/panic.gif'),
('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',WDIR+'image/icons/search.png')
]

#Loading APPS from config doesnt work!!!

#For ExternalApp/VaccaActions use:
# {'$VarName':{'name':'$AppName','classname':'VaccaAction','model':['$Test','$/path/to/icon.png','$launcher']}}
#xrga = AppletDescription('RGA',classname = 'VaccaAction',model=['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01'])
EXTRA_APPS = {
    'xrga':{'name':'RGA','classname':'vacca.panel.VaccaAction',
            'model':['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01']}
    }
    
AttributeFilters = {}
CommandFilters = {}
IconMap = {}