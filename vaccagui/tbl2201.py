import imp,fandango
from vaccagui.beamlines import *

GRID = {
        'column_labels': (
            #'ESTA-EH:BL22/VC/VGCT-06/P2|BL22/VC/VGCT-06/State,'+
            'ESTA-EH:BL22/VC/CCGX-02/Pressure|BL22/VC/CCGX-02/State,'+
            #'IC-EH:BL22/VC/VGCT-07/State|BL22/VC/VGCT-08/State,'+
            'BPM-EH:BL22/VC/CCGX-01/Pressure|BL22/VC/CCGX-01/State,'+
            #VGCT-04 is the MKS937B device
            'PIPE-EH:BL22/VC/VGCT-04/P1|BL22/VC/VGCT-04/State|BL22/VC/IPCT-05/P1|BL22/VC/IPCT-05/State,'+
            'PSHU-OH:BL22/VC/VGCT-03/State|BL22/VC/VGCT-03/P2|BL22/VC/IPCT-04/P2,'+
            'VFM-OH:BL22/VC/VGCT-03/P1|BL22/VC/IPCT-04/P1|BL22/VC/IPCT-04/State,'+
            'FSM2-OH:BL22/VC/IPCT-03/P2,'+
            'DM-OH:BL22/VC/VGCT-02/P2|BL22/VC/IPCT-03/P1,'+
            'MONO-OH:BL22/VC/VGCT-02/P1|BL22/VC/VGCT-02/State|BL22/VC/IPCT-02/P2|BL22/VC/IPCT-02/State,'+
            'FSM-OH:BL22/VC/IPCT-02/P1,'+
            'VCM-OH:BL22/VC/VGCT-01/P2|BL22/VC/IPCT-01/P2|BL22/VC/IPCT-01/State,'+
            'WBAT-OH:BL22/VC/VGCT-01/P1|BL22/VC/VGCT-01/State|BL22/VC/IPCT-01/P1,'+
            'TRU-F22:FE22/VC/VGCT-01/P1|FE22/VC/VGCT-01/State|FE22/VC/IPCT-01/State|FE22/VC/IPCT-01/P1'),
        'delayed': False,
        'frames': False,
        'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|CCG, IonPumps(mbar):IPCT'
    }
