import imp,fandango
from vacca.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE

from vacca.utils import DEFAULT_PATH

WDIR = DEFAULT_PATH

COMPOSER = DEVICE = 'BL00/VC/ALL'
DOMAIN = BL = 'BL00'

GAUGES = [a 
    for d in fandango.get_matching_devices('*00/*/(mvc|vgct)*')
    for a in fandango.get_matching_attributes('%s/p[12]'%d)
    if fandango.tango.check_device(d) and str(getattr(fandango.tango.check_attribute(d+'/state'),'value','UNKNOWN')) not in 'UNKNOWN,FAULT'
    ]

EXTRA_DEVICES = [
    d for d in (
        fandango.get_matching_devices('*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*')+
        fandango.Astor('PyAlarm/*').get_all_devices())
    if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba')) and d.lower().startswith('bl00')
    ]
    
GRID = {
        'column_labels': (
            #'ESTA-EH:BL00/VC/VGCT-06/P2|BL00/VC/VGCT-06/State,'+
            'ESTA-EH:BL00/VC/CCGX-02/Pressure|BL00/VC/CCGX-02/State,'+
            #'IC-EH:BL00/VC/VGCT-07/State|BL00/VC/VGCT-08/State,'+
            'BPM-EH:BL00/VC/CCGX-01/Pressure|BL00/VC/CCGX-01/State,'+
            #VGCT-04 is the MKS937B device
            'PIPE-EH:BL00/VC/VGCT-04/P1|BL00/VC/VGCT-04/State|BL00/VC/IPCT-05/P1|BL00/VC/IPCT-05/State,'+
            'PSHU-OH:BL00/VC/VGCT-03/State|BL00/VC/VGCT-03/P2|BL00/VC/IPCT-04/P2,'+
            'VFM-OH:BL00/VC/VGCT-03/P1|BL00/VC/IPCT-04/P1|BL00/VC/IPCT-04/State,'+
            'FSM2-OH:BL00/VC/IPCT-03/P2,'+
            'DM-OH:BL00/VC/VGCT-02/P2|BL00/VC/IPCT-03/P1,'+
            'MONO-OH:BL00/VC/VGCT-02/P1|BL00/VC/VGCT-02/State|BL00/VC/IPCT-02/P2|BL00/VC/IPCT-02/State,'+
            'FSM-OH:BL00/VC/IPCT-02/P1,'+
            'VCM-OH:BL00/VC/VGCT-01/P2|BL00/VC/IPCT-01/P2|BL00/VC/IPCT-01/State,'+
            'WBAT-OH:BL00/VC/VGCT-01/P1|BL00/VC/VGCT-01/State|BL00/VC/IPCT-01/P1,'+
            'TRU-F00:FE00/VC/VGCT-01/P1|FE00/VC/VGCT-01/State|FE00/VC/IPCT-01/State|FE00/VC/IPCT-01/P1'),
        'delayed': False,
        'frames': False,
        'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|CCG, IonPumps(mbar):IPCT'
    }

EXTRA_PANELS = []
#EXTRA_PANELS.append(('PANIC','panic.gui.AlarmGUI','--'))
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
('PyTangoArchiving.widget.browser.ArchivingBrowser',WDIR+'image/icons/search.png'),
('PyTangoArchiving.widget.ArchivingBrowser.ArchivingBrowser',WDIR+'image/icons/search.png')
]