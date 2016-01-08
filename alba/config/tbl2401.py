import imp,fandango
from vacca.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE

"""
> @TODO: Add an extra NAPP tree with Gauge devices with verbose names:
>  * AC/PC can be kept
>  * Use Analyzer1 for the analyzer chamber gauges
>  * Use BeamEntrance for PBE1/3
>  * Use Pirani, ColdCathode, HotCathode and PIR_RV for eq types
"""


from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath
JDRAW_FILE = wdir('%s/%s-Y.jdw'%(BL,BL))

"""
# Cabling updated 2013-09-19

Common : 
    ipct-01, wbat,sx diagon
    ipct-02  m1,bcc
    ipct-03, mono,4jaw
    ipct-04, m3, YCH
    vgct-01, wbat, m1 ; wbat, m1
    vgct-02, bcc, mono ; bcc, mono
Peem: 
    ipct-05, pipe, pipe
    ipct-06, pipe, sx brf
    ipct-07  kb, sx Io
    vgct-03, m3, peem IC ; m3, peem IC
    vgct-04, PEEM BRFM , KB, ... KB
    vgct-05  peem Io, Napp IC; ...,IC
Napp:
    ipct-08, pipe, fsmm
    ipct-09, sx brf, m4
    ipct-10, Io
    vgct-05  peem Io, Napp Ionization; ...,IC
    vgct-06  napp brfm, napp m4 ; ..., m4
    vgct-07 Io
    
    vgct-eh03-ac
    vgct-eh03-accc
    vgct-eh03-an12
    vgct-eh03-an34
    vgct-eh03-ll
    vgct-eh03-pbe13
    vgct-eh03-pc
"""

compact = lambda txt: list(t.replace(' ','') for t in txt.split('\n') if t.strip())

COMMON_PARTS = compact("""
FE_TRU:  FE24/VC/(VGCT  |  IPCT)-01/P1
ATTE:    BL24/VC/(VGCT  |  IPCT)-01/P1
DIAGON:  BL24/VC/IPCT-01/P2
M1:      BL24/VC/(VGCT-01/P2  |  IPCT-02/P1)
BCC:     (VGCT-02/P1  |  IPCT-02/P2)
MONO:    (VGCT-02/P2  |  IPCT-03/P1)
4J-M3-YCH:    (IPCT-03/P2)|(IPCT-04/P1)|(IPCT-04/P2)
""")
dCOMMON = dict(l.split(':') for l in COMMON_PARTS)

NAPP_PARTS = compact("""
PIPE:    (IPCT-08/P1)
FSMM:    (IPCT-08/P2)
IC:      (VGCT-05/P2)
BRFM:    (VGCT-06/P1  |  IPCT-09/P1)
M4B:     (VGCT-06/P2  |  IPCT-09/P2)
I0:      (VGCT-07/P1  |  IPCT-10/P1)
""")
#AN:      (VGCT-EH03-AN)
#AC:      (VGCT-EH03-AC)
#LL-PC-PB: (VGCT-EH03-(LL|PC|PB))

dNAPP = dict(l.split(':') for l in NAPP_PARTS)

PEEM_PARTS = compact("""
PIPE:    (IPCT-05/P1)
FSMM:    (IPCT-05/P2)
IC:      (VGCT-03/P2  |  IPCT-06/P1)
BRFM:    (VGCT-04/P1  |  IPCT-06/P2)
KB:      (VGCT-04/P2  |  IPCT-07/P1)
I0:      (VGCT-05/P1  |  IPCT-07/P2)
""")
dPEEM = dict(l.split(':') for l in PEEM_PARTS)

COMB = [a+':'+dNAPP[b]+'|'+dPEEM[c] for a,b,c in (['PIPE']*3,['FSMM']*3,['IC']*3,['BRFM']*3,('M4B-KB','M4B','KB'),['I0']*3)]
#COMB += ['%s:%s'%(k,dNAPP[k]) for k in ('AN','AC','LL-PC-PB')]

GRID = {
    'column_labels': ','.join(list(reversed(COMMON_PARTS+COMB))),
    'delayed': False,
    'frames': False,
    'model': '*/(VC|EH)/(IPCT-[01][123456789]|MVC*|VGCT-0[1234567])/(P[12]|Pressure)$',
    'row_labels': 
        'PEEM:'+'|'.join(dPEEM.values())+','+
        'COMMON:'+'|'.join(dCOMMON.values())+','+
        'NAPP:'+'|'.join(dNAPP.values())
    }
    
NAPPGRID = {
    'column_labels': 'AC:((*/AC/*/Value)|(*-AC/P*)),ACCC:*-ACCC/P*,AN12:*-AN12/P*,AN34:*-AN34/P*,LL:*-LL/P*,PBE13:*-PBE13/P*,PC:*-PC/P*',
    'delayed': False,
    'frames': False,
    'labels': False,
    'units': False,
    'model': '(BL24|NAPP)/(VC|AC)/VGCT-(EH03-|CM)*/(P[12345]|Value)$',
    'row_labels': 
        'CC:(ACCC/P1|PBE13/P1|PBE13/P2),'+
        'HC:(AC/P1|AN12/P1|AN34/P1|LL/P1|PC/P1),'+
        'PIR:(AC/P2|ACCC/P[2345]|AN12/P[23]|AN34/P[23]|PBE13/P[45]|PC/P2),'+
        'BAR:(AC/VGCT-CM1|AC/VGCT-CM2)'
    }
    
#print GRID['row_labels']
#print GRID['column_labels']

import vacca
from vacca.utils import wdir
from vacca.grid import get_grid
vacca.NappGrid = lambda grid=NAPPGRID: get_grid(grid)
#EXTRA_WIDGETS = [('vacca.NappGrid',wdir('image/BLGrid.jpg'))]
EXTRA_PANELS = [('NAPP','TaurusGrid',NAPPGRID)]

EXTRA_DEVICES = [
    d for d in (
        fandango.get_matching_devices('*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*')+
        fandango.Astor('PyAlarm/*').get_all_devices())
    if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba'))
    ]

JDRAW_TREE = False

rfamilies = '*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*'
CUSTOM_TREE = {
    '0.CT':'BL*(VC/ALL|CT/ALARMS|PLC-01|FE_AUTO)$',
    '1.FE24':'FE24/VC/*',
    '2.EH02-PEEM':'',
    '3.EH03-NAPP':'(*-EH03-*|NAPP/(AC|VC)/*)',
    '4.MKS937 (ccg+pir)':'BL24*(vgct)-[0-9]+$',
    '5.VarianDUAL (pumps)':'BL24*(ipct)-[0-9]+$',
    '6.Valves':{
        '.OH':'*OH/PNV*',
        'EH01':'*EH01/PNV*',
        'EH02':'*EH02/PNV*',
        'EH03':'*EH03/PNV*',
        },
    '7.BAKEOUTS':'BL*(BAKE|ELOTECH|BK)*',
    }

