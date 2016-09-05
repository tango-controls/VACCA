import imp,fandango
from vaccagui.beamlines import *

GRID = {
        'column_labels': ','.join((
            'EM:(BL13/ct/eps-plc-01/PEN_POW_SIG)',
            'PSHU:(BL13/VC/VGCT-03/P(2|5))|(BL13/VC/IPCT-03/(P2|State))',
            'HFM:(BL13/VC/VGCT-03/P(1|4))|(BL13/VC/IPCT-03/(P1|State))',
            'VFM:(BL13/VC/VGCT-02/P(2|5))|(BL13/VC/IPCT-02/(P2|State))',
            'MONO:(BL13/VC/VGCT-02/P(1|4))|(BL13/VC/IPCT-02/(P1|State))',
            'WBAT:(BL13/VC/VGCT-01/P2)|(BL13/VC/IPCT-01/(P2|State))',
            'LAUE:(BL13/VC/VGCT-01/P(1|4))|(BL13/VC/IPCT-01/(P1|State))',
            'TU:(FE13/VC/VGCT-01/P(1|4))|(FE13/VC/IPCT-01/(P1|State))',
            #'Others:.*'
            )),
        'delayed': False,
        'frames': False,
        'model': '*/*/(IPCT|VGCT|EPS)*/(P[12]|State|PEN_POW_SIG)$',
        'row_labels': 'VcGauges(mbar):VGCT, IonPumps(mbar):IPCT, EM:PEN_POW_SIG',
    }
