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
default.py.ini is a configuration file example of how to specify system-wide defaults for VaccaGUI 

After copying it to default.py this configuration file determines the default, permanent, pre-defined
options for the GUI; modify them to match your default gui options.

Every CONFIG file loaded by vaccagui will override those options redefined on it; 
use default.py for your common options and whatever.py for your in-place customization.
"""

import os,fandango,imp,vacca.utils
from fandango import matchCl,searchCl,replaceCl,CaselessDict,CaselessList,get_matching_devices,get_matching_attributes

print '>'*20+' Loading controls01.py'

#ALL these variables can be re-defined in CONFIG FILE
GUI_NAME = 'VACCA'
WDIR = vacca.utils.WORKING_DIR #imp.find_module('vacca')[1]+'/'
URL_HELP = 'http://www.tango-controls.org/Members/srubio/vacca'
URL_LOGBOOK = 'http://logbook.cells.es/'
VACCA_LOGO = WDIR+'image/icons/nggshow.php.png'
ORGANIZATION_LOGO = WDIR+'image/icons/AlbaLogo.png'

###############################################################################
# Synoptic file

JDRAW_FILE = '' #WDIR+'%s/%s.jdw'%(TARGET,TARGET)
#Enables/disables loading jdraw objects into tree
JDRAW_TREE = True 
#A method that does transformation on signals sent to other widgets.
JDRAW_HOOK = None #lambda s: apply_transform(get_coordinates(s)) 
# Enable multiple selection of objects in Synoptic
#from taurus.qt.qtgui.graphic import TaurusGraphicsScene
#TaurusGraphicsScene.ANY_ATTRIBUTE_SELECTS_DEVICE = True

###############################################################################
# Setup of the tree

#Domain/Target used to generate grids/trees ; domain may be regexp, target should not
DOMAIN = 'BL*'
TARGET = DOMAIN
USE_DEVICE_TREE = True

#Devices not in JDraw or regular expression to be added to the tree

#Custom tree branches are built using nested dictionaries and regular expressions (if empty a jive-like tree is built).
CUSTOM_TREE =\
    {'CT':'BL*(CT|ALARMS|PLC)$',
     'FE':'FE*/VC/*',
     'Valves': {'.OH':'*OH/PNV*',
                'EH01':'*EH01/PNV*',},
     'BAKEOUTS':'BL*(BAKE|BK)*',}

###############################################################################
# Device Panel setup

#PyStateComposer to get Vacuum Profile curves
COMPOSER = '' #'%s/vc/all'%DOMAIN

#Default device to appear in the DevicePanel
DEVICE = 'sys/tg_test/1'
USE_DEVICE_PANEL = True
PANEL_COMMAND = 'taurusdevicepanel --config-file='+WDIR+'default.py'
EXTRA_DEVICES = [DEVICE] #map(bool,set(['%s/VC/ALL'%TARGET,'%s/CT/ALARMS'%TARGET,DEVICE,COMPOSER]))

#Examples of Attribute filters to be applied to DevicePanel
AttributeFilters = {'V-PEN': ['pressure','channelstatus','controller'],}
AttributeFilters['EPS']=[ #You can distribute attributes in different tabs using tuples
    ('Status',['_READY','OPEN_','CLOSE_']),
    ('Signals',['.*_PT.*','was_','paas_','*RGA*']),
    ]
CommandFilters = {'V-PEN': (('on',()),('off',())),} #Second argument of tuple is the list of default arguments
IconMap = {'v-pen':WDIR+'image/equips/icon-pen.gif'} #Will be used in both panel and tree

## Optional:
## If you put filters in a separate file you can load a taurusdevicepanel.py with --config-file=filters.py option
## Then replace previous lines by:
# from vacca.filters import * 

###############################################################################
# Plot setup

#Pressure values to be added to the trend
GAUGES = [] #['bl13/vc/vgct-01/p1','bl13/vc/vgct-01/p2'] 
#sorted(fandango.get_matching_attributes('%s/*/vgct*/p[12]'%DOMAIN.replace('BL','(BL|FE|ID)')))

###############################################################################
# Grid setup

#Grid showing all pressures in rows/columns
GRID = {
    'column_labels': '',
    'delayed': False,
    'frames': False,
    'model': ['%s/VC/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$'%DOMAIN,'%s/V-[^/]*/[0-9]*/(Pressure|State)'%DOMAIN],
    'row_labels':'VcGauges(mbar):(VGCT|PEN), IonPumps(mbar):(IPCT|VARIP)',
    }

#Extra widgets to appear in the NewPanel dialog
EXTRA_WIDGETS = [] #('vacca.VacuumProfile',WDIR+'image/ProfilePlot.jpg'),
EXTRA_PANELS = [] #('vacca.VacuumProfile',WDIR+'image/ProfilePlot.jpg'),
TOOLBARS = [] #[(name,modulename.classname)]

#===============================================================================
# Define which External Applications are to be inserted.
# To define an external application, instantiate an ExternalApp object
# See TaurusMainWindow.addExternalAppLauncher for valid values of ExternalApp
#===============================================================================

from taurus.qt.qtgui.taurusgui.utils import PanelDescription, ExternalApp, ToolBarDescription, AppletDescription

xvacca = ExternalApp(cmdargs=['konqueror',URL_HELP], text="Alba VACuum Controls Application", icon=WDIR+'image/icons/cow-tux.png')
xtrend = ExternalApp(cmdargs=['taurustrend','-a'], text="TaurusTrend")
xjive = ExternalApp(cmdargs=['jive'], text="Jive")#, icon=WDIR+'image/icons/cow-tux.png')
xastor = ExternalApp(cmdargs=['astor'], text="Astor")#, icon=WDIR+'image/icons/cow-tux.png')
#logbook = ExternalApp(cmdargs=['konqueror %s'%URL_LOGBOOK], text="Logbook", icon=WDIR+"image/icons/elog.png")

#===============================================================================
# Define custom applets to be shown in the applets bar (the wide bar that
# contains the logos). To define an applet, instantiate an AppletDescription
# object (see documentation for the gblgui_utils module)
#===============================================================================
    
#Each Applet can be described with a dictionary like this:
#   (name, classname=None, modulename=None, widgetname=None, 
#       sharedDataWrite=None, sharedDataRead=None, model=None, floating=True, **kwargs)
#For ExternalApp/VaccaActions use:
# {'$VarName':{'name':'$AppName','classname':'VaccaAction','model':['$Test','$/path/to/icon.png','$launcher']}}

EXTRA_APPS = {
    #'xrga':{'name':'RGA','classname':'VaccaAction','model':['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01']}
    }
    
#from vacca.panel import VaccaAction
    
xmambo = AppletDescription('Mambo',classname = 'vacca.panel.VaccaAction',model=["Archiving",WDIR+'image/icons/Mambo-icon.png','mambo'],)
xalarms = AppletDescription('Alarms',classname='vacca.panel.VaccaAction',model=['Alarms',WDIR+'image/icons/panic.gif','panic'])
xsnap = AppletDescription('xSnap',classname='vacca.panel.VaccaAction',model=['Snap',WDIR+'image/icons/Crystal_Clear_app_kedit.png','ctsnaps'])
