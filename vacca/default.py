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
from taurus.qt.qtgui.button import TaurusLauncherButton
from vacca.utils import *
from fandango import matchCl,searchCl,replaceCl,CaselessDict,CaselessList,\
    get_matching_devices,get_matching_attributes,get_all_devices,check_device

print '>'*20+' Loading default.py'

#ALL these variables can be re-defined in CONFIG FILE
GUI_NAME = 'VACCA'
WDIR = wdir() #imp.find_module('vacca')[1]+'/'
URL_HELP = 'http://computing.cells.es/services/controls/vacuum'
URL_LOGBOOK = 'http://logbook.cells.es/'
VACCA_LOGO = vpath('image/icons/AlbaLogo.png')
ORGANIZATION = 'TANGO'
ORGANIZATION_LOGO = vpath('image/icons/TangoLogo.png')

###############################################################################
# Synoptic file

JDRAW_FILE = '' #WDIR+'/examples/elinac/linac.jdw' #WDIR+'%s/%s.jdw'%(TARGET,TARGET)
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
DOMAIN = '*test*'
TARGET = DOMAIN
USE_DEVICE_TREE = True

#Devices not in JDraw or regular expression to be added to the tree
EXTRA_DEVICES = [d for d in get_all_devices() if not matchCl('^(tango|dserver)/*',d)]#map(bool,set(['%s/VC/ALL'%TARGET,'%s/CT/ALARMS'%TARGET,DEVICE,COMPOSER]))

#Custom tree branches are built using nested dictionaries and regular expressions (if empty a jive-like tree is built).
CUSTOM_TREE = {} 

# {'CT':'BL*(CT|ALARMS|PLC)$',
#  'FE':'FE*/VC/*',
#  'Valves': {'.OH':'*OH/PNV*',
#             'EH01':'*EH01/PNV*',},
#  'BAKEOUTS':'BL*(BAKE|BK)*',}

###############################################################################
# Device Panel setup

#PyStateComposer to get Vacuum Profile curves
COMPOSER = '' #'%s/vc/all'%DOMAIN

#Default device to appear in the DevicePanel
DEVICE = None # 'sys/tg_test/1' ; tg_test caused segfault in some cases!?
#DEVICE = fandango.first(d for d in get_matching_devices('(sys/tg_test|tango)*')
              #if check_device(d))
USE_DEVICE_PANEL = True
PANEL_COMMAND = 'taurusdevicepanel --config-file='+wdir()+'default.py'

#Examples of Attribute filters to be applied to DevicePanel
AttributeFilters = {'V-PEN': ['pressure','channelstatus','controller'],}
AttributeFilters['EPS-TEST']=[ #You can distribute attributes in different tabs using tuples
    ('Status',['_READY','OPEN_','CLOSE_']),
    ('Signals',['.*_PT.*','was_','paas_','*RGA*']),
    ]
CommandFilters = {'V-PEN': (('on',()),('off',()),('setMode',('START','PROTECT'))),} #Second argument of tuple is the list of default arguments
IconMap = {'v-pen':WDIR+'image/equips/icon-pen.gif'} #Will be used in both panel and tree

## Optional:
## If you put filters in a separate file you can load a taurusdevicepanel.py with --config-file=filters.py option
## Then replace previous lines by:
# from vacca.filters import * 

###############################################################################
# Plot setup

#Pressure values to be added to the logaritmic trend
GAUGES = [] #['bl13/vc/vgct-01/p1','bl13/vc/vgct-01/p2'] 
#sorted(fandango.get_matching_attributes('%s/*/vgct*/p[12]'%DOMAIN.replace('BL','(BL|FE|ID)')))

###############################################################################
# Grid setup

#Grid showing all pressures in rows/columns
GRID = {
    'column_labels': '',
    'delayed': False,
    'frames': False,
    'model': [], 
    #'%s/VC/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$'%DOMAIN,'%s/V-[^/]*/[0-9]*/(Pressure|State)'%DOMAIN],
    'row_labels':'VcGauges(mbar):(VGCT|PEN), IonPumps(mbar):(IPCT|VARIP)',
    }

###############################################################################
# Extra widgets to appear in the NewPanel dialog

EXTRA_WIDGETS = [
        ('panic.gui.AlarmGUI',wdir('image/icons/panic.gif')),
        ('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',wdir('image/widgets/Archiving.png')),
        #('vacca.VacuumProfile',WDIR+'image/ProfilePlot.jpg'),
        ]

###############################################################################
# Extra panels to be loaded at startup
# Extra apps to be added to the right-side Toolbar (loaded only on demand)

EXTRA_PANELS = {}
EXTRA_APPS = fandango.dicts.SortedDict()
from taurus.qt.qtgui.taurusgui.utils import PanelDescription, AppletDescription

LIGHTWEIGHT = True
if not LIGHTWEIGHT:
  
  import vacca.properties
  EXTRA_PANELS['Properties'] = vacca.properties.VaccaPropTable.getPanelDescription('Properties',DEVICE)

  EXTRA_PANELS['PANIC'] = PanelDescription(
      'PANIC','panic.gui.AlarmGUI',model='',#---
      sharedDataWrite={'HighlightInstruments':'devicesSelected'})

  #EXTRA_PANELS.append(('Form','TaurusForm',''))

  try:
      import PyTangoArchiving.widget.browser
      c = PyTangoArchiving.widget.browser.ArchivingBrowser
  except:
      import PyTangoArchiving.widget.ArchivingBrowser
      c = PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget
  EXTRA_PANELS['Finder'] = PanelDescription('Finder',w)
  EXTRA_APPS['Finder'] = {'name': 'Finder','class': c,'icon': wdir('image/icons/search.png')}
  
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

    #'xrga':{'name':'RGA','classname':'VaccaAction','model':['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01']}

EXTRA_APPS['PANIC'] = {'name': 'PANIC',
                'class': vacca.VaccaPanic}
#EXTRA_APPS['Mambo'] = {'name': 'Mambo',
                #'class': lambda:os.system('mambo&'),
                #'icon': wdir('image/icons/Mambo-icon.png')}
EXTRA_APPS['Properties'] = {'class' : vacca.VaccaPropTable}

#EXTRA_APPS['DevicePanel'] = {'class' : vacca.VaccaPanel}
#EXTRA_APPS['Panic']= {'class' : vacca.VaccaPanic       }
#EXTRA_APPS['ExtraDock']= {'class' : Qt.QMainWindow       }    
    
from vacca.panel import VaccaAction
    
#xmambo = AppletDescription('Mambo',classname = 'vacca.panel.VaccaAction',
# model=["Archiving",wdir('vacca/image/widgets/ProfilePlot.png'),'mambo'],)
#xalarms = AppletDescription('Alarms',classname='vacca.panel.VaccaNewPanel',
# model=['Alarms',wdir('vacca/image/icons/panic.gif'),'panic.gui.AlarmGUI'])
#xsnap = AppletDescription('xSnap',classname='vacca.panel.VaccaAction', model=['Snap',vpath('image/widgets/VerticalGrid.jpg'),'ctsnaps'])
#xfinder = AppletDescription('xFinder',classname='vacca.panel.VaccaAction', model=['Attribute Finder',':actions/system-search.svg','ctfinder'])

#button =  TaurusLauncherButton(widget =
#button.setModel('a/b/c') #a device name, which will be given to the
# TaurusAttrForm when clicking

#===============================================================================
# Define which External Applications are to be inserted.
# To define an external application, instantiate an ExternalApp object
# See TaurusMainWindow.addExternalAppLauncher for valid values of ExternalApp
#===============================================================================

TOOLBARS = [] #[(name,modulename.classname)]

MENUS = []
"""
MENUS = [('Tools',[('Jive',lambda:os.system('jive &'),None),])]
"""

from taurus.qt.qtgui.taurusgui.utils import ExternalApp, ToolBarDescription

#xvacca = ExternalApp(cmdargs=['konqueror',URL_HELP], text="Alba VACuum Controls Application", icon=WDIR+'/image/icons/cow-tux.png')
#logbook = ExternalApp(cmdargs=['konqueror %s'%URL_LOGBOOK], text="Logbook", icon=WDIR+"/image/icons/elog.png")
#xtrend = ExternalApp(cmdargs=['taurustrend','-a'], text="Trend")
#xjive = ExternalApp(cmdargs=['jive'], text="Jive")#, icon=WDIR+'/image/icons/cow-tux.png')
#xastor = ExternalApp(cmdargs=['astor'], text="Astor")#, icon=WDIR+'/image/icons/cow-tux.png')

EXTRA_TOOLS = [
  ('Jive',['jive'],vpath('image/icons/TangoLogo.png')),
  ('Trends',['taurustrend','-a'],vpath('image/widgets/PressureTrend.jpg')),
  ]

__doc__ = vacca.get_autodoc(__name__,vars())
