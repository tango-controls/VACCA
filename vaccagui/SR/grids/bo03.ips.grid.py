#!/usr/bin/python

##Just a proof, not the final one, using simulated values
#srubio@cells.es, 2009



# export TANGO_HOST=controls02:10000
# /usr/bin/python /homelocal/sicilia/lib/python/site-packages/tau/widget/taugrid.py  model="BO*/VC/((IP-*)|(PIR*)|(CCG*))/.*[0-9][0-9]" "rows=CCG:CCG,PIR:PIR,IP:IP-" "cols=Q1A:BO01.*(CCG-01|PIR-01|IP-0|IP-1[0-7]),Q1B:BO01.*(CCG-02|IP-[12]|IP-3[01]),Q1LTB:BO01.*(CCG-03|PIR-02|IP-32),Q2A:BO02.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q2B:BO02.*(CCG-02|IP-[123].),Q3A:BO03.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q3B:BO03.*(CCG-02|IP-[123].),Q4A:BO04.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q4B:BO04.*(CCG-02|IP-1[89]|IP-20),Q4BT:BO04.*(PIR-02|IP-2[12]),Q4C:BO04.*(CCG-03|PIR-03|IP-2[3-8]),Q4D+RF:BO04.*(PIR-04|CCG-0[45]|IP-29|IP-3)" &

import tau
from tau.widget import TauGrid
import sys
from PyQt4 import QtGui,QtCore
app = QtGui.QApplication([])
gui = TauGrid()

gui.setRowLabels('CCG:CCG,PIR:PIR,IP:IP-')
gui.setColumnLabels("Q1A:BO01.*(CCG-01|PIR-01|IP-0|IP-1[0-7]),Q1B:BO01.*(CCG-02|IP-[12]|IP-3[01]),Q1LTB:BO01.*(CCG-03|PIR-02|IP-32),Q2A:BO02.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q2B:BO02.*(CCG-02|IP-[123].),Q3A:BO03.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q3B:BO03.*(CCG-02|IP-[123].),Q4A:BO04.*(CCG-01|PIR-01|IP-0.|IP-1[0-7]),Q4B:BO04.*(CCG-02|IP-1[89]|IP-20),Q4BT:BO04.*(PIR-02|IP-2[12]),Q4C:BO04.*(CCG-03|PIR-03|IP-2[3-8]),Q4D+RF:BO04.*(PIR-04|CCG-0[4-9]|IP-29|IP-3)")
gui.setModel("BO*/VC/((IP-*)|(PIR*)|(CCG*))/Pressure")
#gui.showRowFrame('rowframe' in args and args['rowframe'] and True)
#gui.showColumnFrame('colframe' in args and args['colframe'] and True)
#gui.showOthers('others' in args and args['others'] or False)

print "current TauGrid model= %s"%(gui.getModel())
gui.show()
sys.exit(app.exec_())