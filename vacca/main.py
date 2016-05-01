#!/usr/bin/env python
"""
Vacca runner; this file emulates this call:
 >taurusgui vacca
 
Config file (or Property name) is obtained from shell args, then env, 
then properties in this order.

If empty, a DEFAULT profile is created pointing to default.py
 
MAIN CODE FOR PANELS GENERATION IS IN vacca.config SUBMODULE
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

for k,v in os.environ.items():
  if 'VACCA' in k:
    print((k,v))

options = [a for a in args if a.startswith('-')]
files = [a for a in args if a not in options] or [os.getenv('VACCA_CONFIG')]
configs = vu.get_config_properties()

if not configs:
    print('Creating default VACCA properties')
    configs = ['DEFAULT']
    print(configs)
    vu.get_database().put_property('VACCA',{
        'VaccaConfigs':configs})
    vu.get_database().put_property('VACCA',{
        'DEFAULT':['VACCA_CONFIG='+vacca_path+'/default.py']})
    configs = vu.get_config_properties()

if not files or not files[0]: files = [configs.keys()[0]]

dirname = os.getenv('VACCA_DIR') or ''

if files[0] in configs:
    print('Loading %s'%files[0])
    data = vu.get_config_properties(files[0])
    print(data)
    config = data.get('VACCA_CONFIG',files[0])
    dirname = data.get('VACCA_DIR',dirname)
else: 
    config = files[0]

dirname = dirname or os.path.dirname(config) or \
  vu.get_vacca_property('VACCA_DIR',extract=True)

os.environ['VACCA_DIR'] = dirname
os.environ['VACCA_CONFIG'] = config

for k,v in os.environ.items():
  if 'VACCA' in k:
    print((k,v))

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
  
### MAIN CODE FOR PANELS GENERATION IS IN vacca.config SUBMODULE

confname = 'vaccagui'
app = TaurusApplication()
gui = TaurusGui(None, confname=confname)
gui.show()
ret = app.exec_()

taurus.info('Finished execution of TaurusGui')
sys.exit(ret)

