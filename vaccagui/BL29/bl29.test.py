import os,sys,traceback
from fandango.dicts import SortedDict
from fandango.device import get_matching_devices


###############################################################################
# Edit whatever you want below this lines
###############################################################################

#The device that will be shown by default when loading the application
DEVICE = 'BL29/VC/ALL'


#-------------------------------------------------------------------
from PyQt4 import Qt
qapp = Qt.QApplication([])
tg = None

def get_beamline_grid():
    import tau.widget.taugrid
    global tg
    tg = tau.widget.taugrid.TauGrid()
    tg.setRowLabels('VcGauges(mbar):VGCT, IonPumps(mbar):IPCT')
    tg.setColumnLabels(','.join((
        'DISET-EH:BL29/VC/IPCT-06/P2|BL29/VC/IPCT-06/State|BL29/VC/IPCT-07/P1|BL29/VC/IPCT-07/State|BL29/VC/VGCT-02/P2|BL29/VC/VGCT-02/P5|BL29/VC/VGCT-02/State|'+\
            'BL29/VC/VGCT-03/P2|BL29/VC/VGCT-04/P1',
        'MIR-EH:BL29/VC/IPCT-06/P1|BL29/VC/IPCT-06/State',#|BL29/VC/VGCT-03/P1|BL29/VC/VGCT-03/P4|BL29/VC/VGCT-03/State',
        'SLIEX-EH:BL29/VC/IPCT-05/P1|BL29/VC/IPCT-05/State|BL29/VC/VGCT-03/P5|BL29/VC/VGCT-03/State|BL29/VC/VGCT-04/CP2|BL29/VC/VGCT-04/P2|BL29/VC/VGCT-04/State',
        'SLIT-EH:BL29/VC/IPCT-04/P2|BL29/VC/IPCT-04/State',
        'MONO-EH:BL29/VC/IPCT-03/P2|BL29/VC/IPCT-03/State|BL29/VC/IPCT-04/P1|BL29/VC/IPCT-04/State|BL29/VC/VGCT-02/P1|BL29/VC/VGCT-02/P4|BL29/VC/VGCT-02/State',
        'IP75-EH:BL29/VC/IPCT-03/P1|BL29/VC/IPCT-03/State|BL29/VC/IPCT-05/P2|BL29/VC/IPCT-05/State',
        'SLIE-OH:BL29/VC/IPCT-02/P2|BL29/VC/IPCT-02/State|BL29/VC/VGCT-01/P2|BL29/VC/VGCT-01/P5|BL29/VC/VGCT-01/State',
        'IP200-OH:BL29/VC/IPCT-02/P1|BL29/VC/IPCT-02/State',
        'MIR-OH:BL29/VC/IPCT-01/P2|BL29/VC/IPCT-01/State|BL29/VC/VGCT-01/P1|BL29/VC/VGCT-01/P4|BL29/VC/VGCT-01/State',
        'DISET-OH:BL29/VC/IPCT-01/P1|BL29/VC/IPCT-01/State',
        'TRU-F29:FE29/VC/IPCT-01/P1|FE29/VC/IPCT-01/State|FE29/VC/VGCT-01/P1|FE29/VC/VGCT-01/P4|FE29/VC/VGCT-01/State',
        )))    
    #tg.setColumnLabels(','.join([
        #'DISET-EH:(BL29/VC/IPCT-06/P2|BL29/VC/IPCT-07/P1|BL29/VC/VGCT-02/P2|BL29/VC/VGCT-02/P5|'+\
            #'BL29/VC/VGCT-03/P2|BL29/VC/VGCT-04/P1)',
        #'MIR-EH:(BL29/VC/IPCT-06/P1|BL29/VC/VGCT-03/P1|BL29/VC/VGCT-03/P4)',
        #'SLIEX-EH:(BL29/VC/IPCT-05/P1|BL29/VC/VGCT-04/P2)',
        #'SLIT-EH:(BL29/VC/IPCT-04/P2)',
        #'MONO-EH:(BL29/VC/IPCT-03/P2|BL29/VC/IPCT-04/P1|BL29/VC/VGCT-02/P1|BL29/VC/VGCT-02/P4)',
        #'IP75-EH:(BL29/VC/IPCT-03/P1|BL29/VC/IPCT-05/P2)',
        #'SLIE-OH:(BL29/VC/IPCT-02/P2|BL29/VC/VGCT-01/P2|BL29/VC/VGCT-01/P5)',
        #'IP200-OH:(BL29/VC/IPCT-02/P1)',
        #'MIR-OH:(BL29/VC/IPCT-01/P2|BL29/VC/VGCT-01/P1|BL29/VC/VGCT-01/P4)',
        #'DISET-OH:(BL29/VC/IPCT-01/P1)',
        #'TRU-F29:(FE29/VC/IPCT-01/P1|FE29/VC/VGCT-01/P1|FE29/VC/VGCT-01/P4)',
        #]))        
    #tg.load(wdir('BL29/bl29.grid'))
    tg.showRowFrame(False)
    tg.showColumnFrame(False)
    tg.setModel('*/VC/(IPCT|VGCT)*/(P[12]|State)')
    return tg

def POST_HOOK(tg):
    print 'In bl29.rc.py POST_HOOK method ...'
    try:
        #Disabling TauGrid labels/units
        
        tg.showAttributeLabels(False)
        tg.showAttributeUnits(False)
    except:
        print 'POST_HOOK Failed!:\n%s'%traceback.format_exc()
    return
    
w = get_beamline_grid()
w.show()
raw_input()
POST_HOOK(w)
qapp.exec_()