import imp,fandango,traceback
#from vacca.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE
from vacca.utils import *
try:
  from vaccagui.beamlines import *
except:
  from beamlines import *

#options copied from /homelocal/sicilia/lib/python/site-packages/vacca/beamlines.py

#The device that will be shown by default when loading the application
COMPOSER = 'BL01/VC/ALL'
DEVICE = 'BL01/CT/ALARMS'
DOMAIN = BL = COMPOSER.split('/')[0]
URL_HELP = 'http://controls01/vacca/index.html'

print '>'*20+' Loading config for beamline %s'%BL

#DEFINING THE DEVICES IN THE TREE
EXTRA_DEVICES = [
    #'bl00/ct/eps-plc-01','bl00/ct/alarms',
    d for d in (
        fandango.get_matching_devices('(bl|f)*/*(pnv|eps|vfcs|ccg|tpg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*',fullname=False)
        #+fandango.Astor('PyAlarm/*').get_all_devices()
        )
    if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba'))
    ]

#DEFINING THE GAUGES IN THE TREND
GAUGES = fandango.get_matching_attributes('*/vc/vgct-*/p[12]') + [
  'BL01/CT/EPS-PLC-01/X01A0101CC1_VC_CCG_OH01_01A_AF',
  'BL01/CT/EPS-PLC-01/X01A0101CC2_VC_CCG_OH01_02A_AF',]
    
#SYNOPTIC
JDRAW_FILE = wdir('BL01/BL01.jdw')
#imp.find_module('vacca')[1]+'/%s/%s.jdw'%(BL,BL)

#GAUGES = fandango.get_matching_attributes('*/*/*ccg*/pressure')

GRID = {
        'column_labels': ','.join([]),
        'delayed': False,
        'frames': False,
        'model': '(BL*|F*)/(VC|EH)/(IPCT|VGCT|TPG|CCGX|SPBX)*/(P[12345]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|TPG|CCG, IonPumps(mbar):IPCT|SPBX'
    }


EXTRA_PANELS = {}
from taurus.qt.qtgui.taurusgui.utils import PanelDescription
#EXTRA_PANELS['PANIC'] = PanelDescription('PANIC','panic.gui.AlarmGUI',model='',sharedDataWrite={'HighlightInstruments':'devicesSelected'})

#EXTRA_PANELS['EPS'] = PanelDescription('EPS','gui_alfa.epsgui') #,model='',#---
    #sharedDataWrite={'HighlightInstruments':'devicesSelected'})
#EXTRA_PANELS['trends'] = PanelDescription('Trends','vacca.plot.VaccaTrend')

EXTRA_APPS = {}

try:
  import vacca
  #EXTRA_APPS['Properties'] = {'class' : vacca.VaccaPropTable}
  #EXTRA_APPS['DevicePanel'] = {'class' : vacca.VaccaPanel}
  EXTRA_APPS['PANIC']= {'class' : vacca.VaccaPanic       }
  #EXTRA_APPS['ExtraDock']= {'class' : vacca.panel.VaccaDocker       }    
  #EXTRA_APPS['Fandango'] = {'class' : fandango.qt.QEvaluator, 'icon': ':apps/accessories-calculator.svg'}
except: traceback.print_exc()

try:
  from PyQt4 import Qt
  
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
  import AlbaPLC.tools.Widgets
  EXTRA_APPS['SourceBrowser']= {'class' : AlbaPLC.tools.Widgets.SourceBrowser,
                                'icon' : '/homelocal/sicilia/lib/python/site-packages/AlbaPLC/tools/icon/plc.jpg',
                               }    
except: traceback.print_exc()

#('PANIC','panic.gui.AlarmGUI','--')
#EXTRA_PANELS.append(('PANIC','panic.gui.AlarmGUI','--'))
#EXTRA_PANELS.append(('props','vacca.properties.VaccaPropTable','bl00/vc/all'))
#import vacca.properties
#EXTRA_PANELS['myproperties'] = vacca.properties.VaccaPropTable.getPanelDescription('my props','bl00/vc/all')

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


EXTRA_WIDGETS = [
('panic.gui.AlarmGUI',wdir('image/icons/panic.gif')),
('PyTangoArchiving.widget.browser.ArchivingBrowser',':actions/system-search.svg'),
('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',':actions/system-search.svg')
]

rfamilies = '*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*'
myCUSTOM_TREE = {
    '0.CT':'BL*(VC/ALL|CT/ALARMS|PLC-01|FE_AUTO)$',
    '1.FE00':'FE00/VC/*',
    '2.EH02-PEEM':'',
    '3.EH03-NAPP':'*-EH03-*',
    '4.MKS937 (ccg+pir)':'BL00*(vgct)-[0-9]+$',
    '5.VarianDUAL (pumps)':'BL00*(ipct)-[0-9]+$',
    '6.Valves':{
        '.OH':'*OH/PNV*',
        'EH01':'*EH01/PNV*',
        'EH02':'*EH02/PNV*',
        'EH03':'*EH03/PNV*',
        },
    '7.BAKEOUTS':'BL*(BAKE|ELOTECH|BK)*',
    }
