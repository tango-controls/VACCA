import imp,fandango
#from vacca.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE
from vacca.utils import *
WDIR = VACCA_DIR

#options copied from /homelocal/sicilia/lib/python/site-packages/vacca/beamlines.py

#The device that will be shown by default when loading the application
COMPOSER = DEVICE = fandango.get_matching_devices('BL00/VC/ALL')[0]
DOMAIN = BL = COMPOSER.split('/')[0]

print '>'*20+' Loading config for beamline %s'%BL

#DEFINING THE DEVICES IN THE TREE
EXTRA_DEVICES = [
    d for d in (
        fandango.get_matching_devices('(bl|fe)00*(pnv|eps|vfcs|ccg|tpg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*',fullname=False)
        #+fandango.Astor('PyAlarm/*').get_all_devices()
        )
    if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba'))
    ]
#print 'EXTRA_DEVICES: %s'%EXTRA_DEVICES

#DEFINING THE GAUGES IN THE TREND
GAUGES = [
    'BL00/VC/VGCT-01/P1','BL00/VC/VGCT-01/P2','BL00/VC/VGCT-02/P1','BL00/VC/VGCT-02/P2','BL00/VC/TPG-01/P1','BL00/CT/EPS-PLC-01/mir_oh01_01_pt',
    ]
    
#SYNOPTIC
JDRAW_FILE = WDIR+'/examples/bl00/BL00/BL00.jdw'
#imp.find_module('vacca')[1]+'/%s/%s.jdw'%(BL,BL)

#GAUGES = fandango.get_matching_attributes('*/*/*ccg*/pressure')

GRID = {
        'column_labels': ','.join([
            'TXM:(BL00/VC/TPG-01/P1)',
            'DIAG2:(BL00/VC/IPCT-04/P2)',
            'DPS:(BL00/VC/IPCT-03/P2)',
            'M4:(BL00/VC/VGCT-02/P2)|(BL00/VC/IPCT-04/P1)',
            'MONO:(BL00/VC/VGCT-02/P1)|(BL00/VC/IPCT-03/P1)',
            'DIAG1:(BL00/VC/IPCT-02/P2)',
            'JJ:(BL00/VC/VGCT-03/P1)',
            'M2:(BL00/VC/VGCT-01/P2)|(BL00/VC/IPCT-02/P1)',
            'M1:(BL00/VC/VGCT-01/P1)|(BL00/VC/IPCT-01/P2)',
            'WBD:(BL00/VC/IPCT-01/P1)',
            'FE:FE00/VC/(VG|IP)CT-01/P(1|2)']),
        'delayed': False,
        'frames': False,
        'model': '(BL00|FE00)/(VC|EH)/(IPCT|VGCT|TPG|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|TPG|CCG, IonPumps(mbar):IPCT'
    }


EXTRA_PANELS = {}
from taurus.qt.qtgui.taurusgui.utils import PanelDescription
EXTRA_PANELS['PANIC'] = PanelDescription(
    'PANIC','panic.gui.AlarmGUI',model='',#---
    sharedDataWrite={'HighlightInstruments':'devicesSelected'})


#('PANIC','panic.gui.AlarmGUI','--')
#EXTRA_PANELS.append(('PANIC','panic.gui.AlarmGUI','--'))
#EXTRA_PANELS.append(('props','vacca.properties.VaccaPropTable','bl00/vc/all'))
#import vacca.properties
#EXTRA_PANELS['myproperties'] = vacca.properties.VaccaPropTable.getPanelDescription('my props','bl00/vc/all')

#EXTRA_PANELS.append(('Form','TaurusForm',''))
#try:
    #from PyTangoArchiving.widget.browser import ArchivingBrowser
    #w = 'PyTangoArchiving.widget.browser.ArchivingBrowser'
#except:
    #from PyTangoArchiving.widget.ArchivingBrowser import ModelSearchWidget
    #w = 'PyTangoArchiving.widget.ArchivingBrowser.ModelSearchWidget'
#EXTRA_PANELS.append(('Finder',w,''))

EXTRA_WIDGETS = [
('panic.gui.AlarmGUI',WDIR+'image/icons/panic.gif'),
('PyTangoArchiving.widget.browser.ArchivingBrowser',WDIR+'image/icons/search.png'),
('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',WDIR+'image/icons/search.png')
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
