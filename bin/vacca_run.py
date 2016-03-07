#!/usr/bin/env python
"""
Vacca runner; this file emulates this call:
 >taurusgui vacca
"""

import sys
import taurus
import re
from taurus.core.util import argparse
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.taurusgui import TaurusGui

args = sys.argv()

def remove_last_config(filename):
    print('vacca.remove_last_config(%s)'%filename)
    lines = open(filename).readlines()
    sections = dict((l.strip(),i) for i,l in enumerate(lines) 
                    if re.match('[\[][a-zA-Z]*[\]]',l))
    sections['[End]'] = len(lines)
    begin = sections['[General]']
    end = min(i for i in sections.values() if i>begin)
    fo = open(filename,'w')
    fo.writelines(lines[:begin]+lines[end:])
    fo.close()  

folder = os.getenv('HOME')+'/.config/VACCA/'
if '--clean' in args:
  os.remove(folder+'*.ini')
elif '--reset' in args:
  inits = [a for a in os.walk(f).next()[2] if a.endswith('.ini')]
  [remove_last_config(folder+filename) for filename in inits]

confname = 'vaccagui'
app = TaurusApplication()
gui = TaurusGui(None, confname=confname)
gui.show()
ret = app.exec_()

taurus.info('Finished execution of TaurusGui')
sys.exit(ret)

