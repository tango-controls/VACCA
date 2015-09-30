#!/usr/bin/env python
"""
Vacca runner; this file emulates this call:
 >taurusgui vacca
"""

import sys
import taurus
from taurus.core.util import argparse
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.taurusgui import TaurusGui

confname = 'vaccagui'
app = TaurusApplication()
gui = TaurusGui(None, confname=confname)
gui.show()
ret = app.exec_()

taurus.info('Finished execution of TaurusGui')
sys.exit(ret)

