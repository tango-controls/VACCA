#!/usr/bin/python

##Just a proof, not the final one, using simulated values
#srubio@cells.es, 2009

import tau
from tau.widget import TauGrid
import sys,re
from PyQt4 import QtGui,QtCore
app = QtGui.QApplication([])
gui = TauGrid()

args = sys.argv[1:]
show_all = (not args or args[0].lower()=='all')
all_models = \
  "Q1A:BO01.*(CCG-01|PIR-01|IP-0|IP-1[0-7]),Q1B:BO01.*(CCG-02|IP-[12]|IP-3[01]),Q1LTB:BO01.*(CCG-03|PIR-02|IP-32),"+\
  "Q2A:BO02.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q2B:BO02.*(CCG-02|IP-[123].),"+\
  "Q3A:BO03.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q3B:BO03.*(CCG-02|IP-[123].),"+\
  "Q4A:BO04.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q4B:BO04.*(CCG-02|IP-1[89]|IP-20),Q4BT:BO04.*(PIR-02|IP-2[12]),Q4C:BO04.*(CCG-03|PIR-03|IP-2[3-8]),Q4D+RF:BO04.*(PIR-04|CCG-0[4-9]|IP-29|IP-3)" 
if show_all:
  gui.setRowLabels('CCG:CCG,PIR:PIR,IP:IP-')
  gui.setColumnLabels(all_models)
  gui.setModel("BO*/VC/((IP-*)|(PIR*)|(CCG*))/Pressure")
elif re.match('bo0[1-4]',args[0].lower()):
  gui.setRowLabels('CCG:CCG,PIR:PIR,IP:IP-')
  gui.setColumnLabels(','.join(s for s in all_models.split(',') if args[0].upper() in s))
  gui.setModel("%s/VC/((IP-*)|(PIR*)|(CCG*))/Pressure"%(args[0].upper()))
elif args[0].lower().startswith('lt'):
  gui.setRowLabels('CCG:CCG,PIR:PIR,IP:IP-')
  gui.setColumnLabels( "LT01:LT01.*(CCG-|IP-),LT02:LT02.*(CCG-|IP-)")
  gui.setModel("LT.*/VC/((IP-*)|(PIR*)|(CCG*))/Pressure")

gui.showRowFrame(show_all or False)
gui.showColumnFrame(show_all or False)
gui.showOthers(show_all or False)
#gui.setTitle(args and (args[0]+' Ion Pumps') or '')
gui.setWindowTitle((args and args[0] or '')+' Ion Pumps')
gui.resize(QtCore.QSize(gui.table.size().height()+50,gui.table.size().width()+50))

print "current TauGrid model= %s"%(gui.getModel())
gui.show()
sys.exit(app.exec_())