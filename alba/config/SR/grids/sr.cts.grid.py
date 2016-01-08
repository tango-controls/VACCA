#!/usr/bin/python

##Just a proof, not the final one, using simulated values
#srubio@cells.es, 2009

import tau
from tau.widget import TauGrid
import sys
from PyQt4 import QtGui,QtCore
app = QtGui.QApplication([])
gui = TauGrid()
gui.setWindowTitle('Status of ALBA SR Vacuum Controllers')

tau.setLogLevel(tau.core.utils.Logger.Debug)
gui.setColumnLabels('VGCT:VGCT,Gauges:CCG|PIR,IPCT:IPCT,SPBX:SPBX,Pumps:IP-')
gui.setRowLabels(','.join(['SR%02d'%i for i in range(1,17)]))
gui.setModel("SR*/VC/ALL/.*(VGCT|IPCT|SPBX)*")
gui.showRowFrame(False)
gui.showColumnFrame(False)
gui.showOthers(False)

print "current TauGrid model= %s"%(gui.getModel())
gui.show()
sys.exit(app.exec_())