import imp,fandango
from vacca.beamlines import BL,COMPOSER,EXTRA_DEVICES,DEVICE,DOMAIN,GAUGES,JDRAW_FILE

GRID = {
        'column_labels': ','.join([
            'PH-SHUTTER:BL04/VC/VGCT-03/P1|BL04/VC/IPCT-04/P2',
            '2nd-COLL:FE04/VC/VGCT-01/P2|BL04/VC/IPCT-04/P1',
            'MONO:BL04/VC/VGCT-02/P2|BL04/VC/IPCT-03/P2',
            'FLUO1:BL04/VC/IPCT-03/P1',
            '6w-BLVS:BL04/VC/VGCT-03/P2|BL04/VC/IPCT-02/P2',
            'MIRROR:BL04/VC/VGCT-02/P1|BL04/VC/IPCT-02/P1',
            'WBATT:BL04/VC/VGCT-01/P2|BL04/VC/IPCT-01/P2',
            'FILTER:BL04/VC/VGCT-01/P1|BL04/VC/IPCT-01/P1',
            'FE:FE04/VC/(VGCT-01/P1|IPCT-01/P1)']
            ),
        'delayed': False,
        'frames': False,
        'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|CCG, IonPumps(mbar):IPCT'
    }
