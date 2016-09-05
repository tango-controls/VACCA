import imp,fandango
from vaccagui.beamlines import *


raise Exception('DEPRECATED BY bl09_vacca.py')

#GAUGES = fandango.get_matching_attributes('*/*/*ccg*/pressure')

GRID = {
        'column_labels': ','.join([
            'TXM:(BL09/VC/VGCT-03/P2)',
            'DIAG2:(BL09/VC/IPCT-04/P2)',
            'DPS:(BL09/VC/IPCT-03/P2)',
            'M4:(BL09/VC/VGCT-02/P2)|(BL09/VC/IPCT-04/P1)',
            'MONO:(BL09/VC/VGCT-02/P1)|(BL09/VC/IPCT-03/P1)',
            'DIAG1:(BL09/VC/IPCT-02/P2)',
            'JJ:(BL09/VC/VGCT-03/P1)',
            'M2:(BL09/VC/VGCT-01/P2)|(BL09/VC/IPCT-02/P1)',
            'M1:(BL09/VC/VGCT-01/P1)|(BL09/VC/IPCT-01/P2)',
            'WBD:(BL09/VC/IPCT-01/P1)',
            'FE:FE09/VC/(VG|IP)CT-01/P(1|2)']),
        'delayed': False,
        'frames': False,
        'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|CCG, IonPumps(mbar):IPCT'
    }
