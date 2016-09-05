import imp,fandango
from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath
from vaccagui.beamlines import *

JDRAW_FILE = wdir('%s/%s-schema.jdw'%(BL,BL))

GRID = {
        #'column_labels': ','.join([
            #'BLVS-3: (bl11/vc/vgct-04/(P2|State))',
            #'BLVS-2: (bl11/vc/vgct-04/(P1|State))|(bl11/vc/ipct-05/(P2|State))',
            #'PSH: (bl11/vc/vgct-03/(P2|State))|(bl11/vc/ipct-05/(P1|State))',
            #'DIFF-2: (bl11/vc/vgct-03/(P1|State))|(bl11/vc/ipct-04/(P2|State))',
            #'MIRR: (bl11/vc/vgct-02/(P2|State))|(bl11/vc/ipct-04/(P1|State))',
            #'DIFF-1: (bl11/vc/vgct-02/(P1|State))|(bl11/vc/ipct-03/(P2|State))',
            #'ATT: (bl11/vc/ipct-03/(P1|State))',
            #'DCM: (bl11/vc/vgct-01/(P2|State))|(bl11/vc/ipct-02/(P2|State))',
            #'PUMP-2: (bl11/vc/ipct-02/(P1|State))',
            #'FMASK: (bl11/vc/ipct-01/(P2|State))',
            #'PUMP-1: (bl11/vc/ipct-01/(P1|State))',
            #'BLVS-1: (bl11/vc/vgct-01/(P1|State))',
            #'TU: (fe11/vc/vgct-01/(P1|State))|(fe11/vc/ipct-01/(P1|State))']
            #),
        'column_labels': ','.join([
            'BLVS-3: (bl11/vc/vgct-04/(P2|State))',
            'BLVS-2: (bl11/vc/vgct-04/(P1|State))|(bl11/vc/ipct-05/(P2|State))',
            'PSH: (bl11/vc/vgct-03/(P2|State))|(bl11/vc/ipct-05/(P1|State))',
            'DIFF-2: (bl11/vc/vgct-03/(P1|State))|(bl11/vc/ipct-04/(P2|State))',
            'MIRR: (bl11/vc/vgct-02/(P2|State))|(bl11/vc/ipct-04/(P1|State))',
            'DIFF-1: (bl11/vc/vgct-02/(P1|State))|(bl11/vc/ipct-03/(P2|State))',
            'ATT: (bl11/vc/ipct-03/(P1|State))',
            'DCM: (bl11/vc/vgct-01/(P2|State))|(bl11/vc/ipct-02/(P2|State))',
            'PUMP-2: (bl11/vc/ipct-02/(P1|State))',
            'FMASK: (bl11/vc/ipct-01/(P2|State))',
            'PUMP-1: (bl11/vc/ipct-01/(P1|State))',
            'BLVS-1: (bl11/vc/vgct-01/(P1|State))',
            'TU: (fe11/vc/vgct-01/(P1|State))|(fe11/vc/ipct-01/(P1|State))']
            ),
        'delayed': False,
        'frames': False,
        'model': '*/(VC|EH)/(IPCT|VGCT|CCGX)*/(P[12]|Pressure|State)$',
        'row_labels': 'VcGauges(mbar):VGCT|CCG, IonPumps(mbar):IPCT'
    }

