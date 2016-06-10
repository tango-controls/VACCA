import imp,fandango,os,traceback
from vaccagui.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE
from vaccagui.filters import *

DOMAIN = 'BL00'
COMPOSER = 'BL00/VC/ALL'
DEVICE = 'BL00/CT/ALARMS'

JDRAW_FILE = 'BL00/BL29.jdw'


GRID = {
    'column_labels': 
        ','.join((
        'DISET-EH:BL00/VC/IPCT-06/P2|BL00/VC/IPCT-06/State|BL00/VC/IPCT-07/P1|BL00/VC/IPCT-07/State|BL00/VC/VGCT-02/P2|BL00/VC/VGCT-02/P5|BL00/VC/VGCT-02/State|'+\
            'BL00/VC/VGCT-03/P2|BL00/VC/VGCT-04/P1',
        'MIR-EH:BL00/VC/IPCT-06/P1|BL00/VC/IPCT-06/State|BL00/VC/VGCT-03/P1|BL00/VC/VGCT-03/P4|BL00/VC/VGCT-03/State',
        'SLIEX-EH:BL00/VC/IPCT-05/P1|BL00/VC/IPCT-05/State|BL00/VC/VGCT-03/P5|BL00/VC/VGCT-03/State|BL00/VC/VGCT-04/CP2|BL00/VC/VGCT-04/P2|BL00/VC/VGCT-04/State',
        'SLIT-EH:BL00/VC/IPCT-04/P2|BL00/VC/IPCT-04/State',
        'MONO-EH:BL00/VC/IPCT-03/P2|BL00/VC/IPCT-03/State|BL00/VC/IPCT-04/P1|BL00/VC/IPCT-04/State|BL00/VC/VGCT-02/P1|BL00/VC/VGCT-02/P4|BL00/VC/VGCT-02/State',
        'IP75-EH:BL00/VC/IPCT-03/P1|BL00/VC/IPCT-03/State|BL00/VC/IPCT-05/P2|BL00/VC/IPCT-05/State',
        'SLIE-OH:BL00/VC/IPCT-02/P2|BL00/VC/IPCT-02/State|BL00/VC/VGCT-01/P2|BL00/VC/VGCT-01/P5|BL00/VC/VGCT-01/State',
        'IP200-OH:BL00/VC/IPCT-02/P1|BL00/VC/IPCT-02/State',
        'MIR-OH:BL00/VC/IPCT-01/P2|BL00/VC/IPCT-01/State|BL00/VC/VGCT-01/P1|BL00/VC/VGCT-01/P4|BL00/VC/VGCT-01/State',
        'DISET-OH:BL00/VC/IPCT-01/P1|BL00/VC/IPCT-01/State',
        'TRU-F29:FE29/VC/IPCT-01/P1|FE29/VC/IPCT-01/State|FE29/VC/VGCT-01/P1|FE29/VC/VGCT-01/P4|FE29/VC/VGCT-01/State',
        )),
    'delayed': False,
    'frames': False,
    'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
    'row_labels':'VcGauges(mbar):VGCT, IonPumps(mbar):IPCT',
    }

try:
  from PyQt4 import Qt
except: traceback.print_exc()

EXTRA_PANELS = {}
EXTRA_APPS = {}
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

#EXTRA_PANELS['PANIC'] = PanelDescription('PANIC','panic.gui.AlarmGUI',model='',sharedDataWrite={'HighlightInstruments':'devicesSelected'})
try:
  import vacca
  #EXTRA_APPS['Properties'] = {'class' : vacca.VaccaPropTable}
  #EXTRA_APPS['DevicePanel'] = {'class' : vacca.VaccaPanel}
  EXTRA_APPS['PANIC']= {'class' : vacca.VaccaPanic       }
  #EXTRA_APPS['ExtraDock']= {'class' : vacca.panel.VaccaDocker       }    
  #EXTRA_APPS['Fandango'] = {'class' : fandango.qt.QEvaluator, 'icon': ':apps/accessories-calculator.svg'}
except: traceback.print_exc()

try:
  import sys
  #sys.path.insert(0,'/homelocal/srubio/PROJECTS/PLCs/EPS-BL09/trunk/PLC_GUI')
  sys.path.insert(0,'/homelocal/sicilia/applications/EPS_GUI/PLC_GUI')
  import gui_alfa
  EXTRA_APPS['EPS']= {'class' : gui_alfa.epsgui,
                      'icon' : '/homelocal/sicilia/lib/python/site-packages/AlbaPLC/tools/icon/Plc_equipment.jpg',
                      }    
  sys.path.append('/homelocal/srubio/PROJECTS/PLCs/DeviceServers/')
  #import AlbaPLC.tools.Widgets
  #EXTRA_APPS['SourceBrowser']= {'class' : AlbaPLC.tools.Widgets.SourceBrowser,
                                #'icon' : '/homelocal/sicilia/lib/python/site-packages/AlbaPLC/tools/icon/plc.jpg',
                               #}    
except: traceback.print_exc()

#EXTRA_PANELS.append(('Form','TaurusForm',''))
try:
    #from PyTangoArchiving.widget.browser import ArchivingBrowser
    #w = 'PyTangoArchiving.widget.browser.ArchivingBrowser'
    import PyTangoArchiving.widget.browser
    c = PyTangoArchiving.widget.browser.ArchivingBrowser
except:
    #from PyTangoArchiving.widget.ArchivingBrowser import ModelSearchWidget
    #w = 'PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget'
    import PyTangoArchiving.widget.ArchivingBrowser
    c = PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget
#EXTRA_PANELS['Finder'] = PanelDescription('Finder',w)
EXTRA_APPS['Finder'] = {'name': 'Finder','class': c,'icon': wdir('image/icons/search.png')}

