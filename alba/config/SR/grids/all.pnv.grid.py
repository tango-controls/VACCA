#!/usr/bin/python

##Just a proof, not the final one, using simulated values
#srubio@cells.es, 2009

import tau
from tau.widget import TauGrid
import sys
from PyQt4 import QtGui,QtCore

app = QtGui.QApplication([])
gui = TauGrid()
gui.setWindowTitle('Status of ALBA PLCValves')

model="*/VC/*PNV-*/Status" 
cols="/PNV,/SPNV" 
rows="LT*,BO01,BO02,BO03,BO04,BT,SR01,SR02,SR03,SR04,SR05,SR06,SR07,SR08,SR09,SR10,SR11,SR12,SR13,SR14,SR15,SR16"

#tau.setLogLevel(tau.core.utils.Logger.Debug)
gui.setColumnLabels(cols)
gui.setRowLabels(rows)
gui.setModel(model)

gui.showRowFrame(False)
gui.showColumnFrame(False)
gui.showOthers(False)

print "current TauGrid model= %s"%(gui.getModel())
gui.show()
sys.exit(app.exec_())

