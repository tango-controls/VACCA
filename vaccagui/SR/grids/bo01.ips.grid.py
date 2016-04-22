#!/usr/bin/python

##Just a proof, not the final one, using simulated values
#srubio@cells.es, 2009

import tau
from tau.widget import TauGrid
import sys
from PyQt4 import QtGui,QtCore
app = QtGui.QApplication([])
gui = TauGrid()

gui.setColumnLabels('CCG:CCG,PIR:PIR,IP:IP-')
gui.setRowLabels("Q1A:BO01.*(CCG-01|PIR-01|IP-0|IP-1[0-7]),Q1B:BO01.*(CCG-02|IP-[12]|IP-3[01]),Q1LTB:BO01.*(CCG-03|PIR-02|IP-32)")
gui.setModel("BO01/VC/((IP-*)|(PIR*)|(CCG*))/Pressure")
gui.showRowFrame(False)
gui.showColumnFrame(False)
gui.showOthers(False)

print "current TauGrid model= %s"%(gui.getModel())
gui.show()
sys.exit(app.exec_())