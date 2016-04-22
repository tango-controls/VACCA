#!/usr/bin/env python
"""
Vacca runner; this file emulates this call:
 >taurusgui vacca
"""

import sys,os,re,time,imp,traceback
import taurus
from taurus.core.util import argparse
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.taurusgui import TaurusGui

args = sys.argv[1:]

import vacca 
import vacca.utils as vu


vacca_path = imp.find_module('vacca')[1]
os.environ['VACCA_PATH'] = vacca_path
#Adding default vaccagui at the end of pythonpath
sys.path.append(vacca_path+'/ini') 

options = [a for a in args if a.startswith('-')]
files = [a for a in args if a not in options]
configs = vu.get_vacca_property('VaccaConfigs',False)
if not configs:
    print('Creating default VACCA properties')
    configs = ['DEFAULT']
    vu.get_database().put_property('VACCA',{
        'VaccaConfigs':configs},False)
    vu.get_database().put_property('VACCA',{
        'DEFAULT':['VACCA_CONFIG='+vacca_path+'/default.py']},False)
if not files: files = [configs[0]]

if files[0] in configs:
    print('Loading %s'%files[0])
    data = vu.get_vacca_property(files[0],False)
    print(data)
    data = dict(l.split('=',1) for l in data)
    config = data.get('VACCA_CONFIG',files[0])
else: config = files[0]    

os.environ['VACCA_CONFIG'] = config
os.environ['VACCA_DIR'] = os.path.dirname(config)
os.chdir(os.environ['VACCA_DIR'])
print(dict((k,v) for k,v in os.environ.items() if 'VACCA' in k))

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

