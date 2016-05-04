"""
THIS FILE JUST IS A DROP-IN FOR USEFUL VACCA RECIPES
"""

print '>'*20+' Loading %s'%__name__

from vacca.utils import DEFAULT_PATH,wdir,vpath,get_os_launcher
from vacca.default import *

WDIR = DEFAULT_PATH
DEVICE = 'lab/vc/vgct-02'
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


#Devices not in JDraw or regular expression to be added to the tree
EXTRA_DEVICES = [d for d in get_all_devices() if not matchCl('^(tango|dserver)/*',d)]

#EXTRA_PANELS['PANIC','panic.gui.AlarmGUI','--'))
#EXTRA_PANELS.append(('Form','TaurusForm',''))

#BAD IDEA , SHOULD BE AN APP!
#EXTRA_PANELS['PANIC'] = PanelDescription(
    #'PANIC','panic.gui.AlarmGUI',model='',#---
    #sharedDataWrite={'HighlightInstruments':'devicesSelected'})

PANEL_COMMAND = 'taurusdevicepanel --config-file='+WDIR+'default.py'

try:
    from PyTangoArchiving.widget.browser import ArchivingBrowser
    w = 'PyTangoArchiving.widget.browser.ArchivingBrowser'
except:
    from PyTangoArchiving.widget.ArchivingBrowser import ModelSearchWidget
    w = 'PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget'
#EXTRA_PANELS['Finder'] = ('Finder',w,'')

EXTRA_WIDGETS = [
('panic.gui.AlarmGUI',WDIR+'image/icons/panic.gif'),
('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',WDIR+'image/icons/search.png')
]

#Extra widgets to appear in the NewPanel dialog
EXTRA_WIDGETS = [
        ('panic.gui.AlarmGUI',wdir('image/icons/panic.gif')),
        ('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',wdir('image/widgets/Archiving.png')),
    ] #('vacca.VacuumProfile',WDIR+'image/ProfilePlot.jpg'),

EXTRA_PANELS = {}
from taurus.qt.qtgui.taurusgui.utils import PanelDescription
#EXTRA_PANELS['PANIC'] = PanelDescription(
    #'PANIC','panic.gui.AlarmGUI',model='',#---
    #sharedDataWrite={'HighlightInstruments':'devicesSelected'})

#Loading APPS from config doesnt work!!!

#For ExternalApp/VaccaActions use:
# {'$VarName':{'name':'$AppName','classname':'VaccaAction','model':['$Test','$/path/to/icon.png','$launcher']}}
#xrga = AppletDescription('RGA',classname = 'VaccaAction',model=['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01'])
EXTRA_APPS.update({
    #'xrga':{'name':'RGA','classname':'vacca.panel.VaccaAction',
            #'model':['RGA',WDIR+'image/equips/icon-rga.gif']+['rdesktop -g 1440x880 ctrga01']}
    })

EXTRA_TOOLS = [
  ('Jive',['jive'],vpath('image/icons/TangoLogo.png')),
  ('Trends',['taurustrend','-a'],vpath('image/widgets/PressureTrend.jpg')),
  ]
  
EXTRA_APPS['Fandango'] = {'name':'QEval',
                'class':fandango.qt.QEvaluator,
                'icon':':apps/accessories-calculator.svg'}

EXTRA_APPS['PANIC'] = {'name': 'PANIC',
                'class': vacca.VaccaPanic}

EXTRA_APPS['Mambo'] = {'name': 'Mambo',
                'class': get_os_launcher('mambo'),
                'icon': wdir('image/icons/Mambo-icon.png')}
EXTRA_APPS['Finder'] = {'name': 'Finder',
                'class': get_os_launcher('taurusfinder'),
                'icon': wdir('image/icons/search.png')}

try:
  print 'Loading filters!!!'
  from vaccagui.filters import *
  IconMap['MKS'] = wdir('image/equips/icon-vgct.gif')
except:
  traceback.print_exc()