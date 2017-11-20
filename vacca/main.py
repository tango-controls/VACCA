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

args = sys.argv[1:]
files = []

__doc__ = """

The file vacca/main.py is the vaccagui launcher 

It creates the taurusgui environment and sets all environment variables.

vaccagui usage
--------------

Launching vacca, loading configuration from a target.py:

  > vaccagui [target.py or $CONFIG] [$OPTION=...]
  
  $CONFIG will load values from VACCA.$CONFIG property in the database
  
  $OPTION=... can be used to override values declared properties or target.py
  
Environment variables (optional, will be initialized in vacca/main.py):

  VACCA_CONFIG : if set, equivalent to passing target.py as argument
  VACCA_DIR : directory to resources needed by target.py (target.py folder by default)
  VACCA_PATH : path to vacca module (initialized by imp.find_module())
  
  If not set, default values are those set as VACCA properties in Tango DB.

Reset of QSettings files:

  > vaccagui --reset   #The last saved perspective will be removed    
  > vaccagui --clean   #All the .ini files will be removed
  
Other options:
  > vaccagui --helps   #Prints this text
  > vaccagui --list    #Prints available configurations
    
"""

if args and args[0].strip('- ') == 'help':
  print(__doc__)
  sys.exit(0)
  
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

options = [a for a in args if a.startswith('-')]
values = [a for a in args if '=' in a]

if '--clean' in args:
  print('Removing last vacca configs (%s/*.ini)'%folder)
  os.remove(folder+'*.ini')
  if len(args)==1: sys.exit(0)
  
elif '--reset' in args:
  inits = [a for a in os.walk(f).next()[2] if a.endswith('.ini')]
  print('Removing last vacca configs (%s)'%inits)
  [remove_last_config(folder+filename) for filename in inits]
  if len(args)==1: sys.exit(0)
  
elif '--help' in args or '-h' in args or '-?' in args:
  print(__doc__)
  sys.exit(0)
  
elif '--list' in args:
  import vacca.utils as vu
  configs = vu.get_config_properties()
  print('\nVaccaConfigs:')
  print('\n\t'+'\n\t'.join(configs)+'\n')
  sys.exit(0)
  
if '--panel' not in args:
  files = [a for a in args if a not in options+values]  
  
files = files or  [os.getenv('VACCA_CONFIG')]
  
###############################################################################

print('-'*80)
print("In vacca.main(%s) ..."%args)
  
###############################################################################
# Delayed imports

import taurus
from taurus.core.util import argparse
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.taurusgui import TaurusGui

###################################################################### 
# Set tangoFormatter as default formatter 
try: 
    from taurus.core.tango.util import tangoFormatter 
    from taurus.qt.qtgui.base import TaurusBaseComponent 
    TaurusBaseComponent.FORMAT = tangoFormatter 
except: 
    pass 
######################################################################

import vacca.utils as vu
import vacca 

configs = vu.get_config_properties() or vu.create_config_properties()

if not files or not files[0]: files = [configs.keys()[0]]

dirname = os.getenv('VACCA_DIR') or ''
config = os.getenv('VACCA_CONFIG') or ''

if files[0] in configs:
    print('Loading %s'%files[0])
    data = vu.get_config_properties(files[0])
    config = config or data.get('VACCA_CONFIG',files[0])
    dirname = dirname or data.get('VACCA_DIR',dirname)
else: 
    config = config or files[0]
    
if os.path.isfile(config):
  config = os.path.abspath(config)
    
elif config:
    try:
      import imp
      print('Loading %s as python module'%config)
      config = imp.find_module(config.replace('.','/'))[1]
      dirname = os.path.dirname(config)
    except:
      pass

dirname = dirname or os.path.dirname(config) or \
  vu.get_vacca_property('VACCA_DIR',extract=1) or ''

vu.VACCA_DIR = os.environ['VACCA_DIR'] = dirname
vu.VACCA_CONFIG = os.environ['VACCA_CONFIG'] = config

print('Vacca Environment variables (vacca.main):')
print('\n'.join(map(str,(t for t in os.environ.items() if 'VACCA' in t[0]))))

### MAIN CODE FOR PANELS GENERATION IS IN vacca.config SUBMODULE
print '-'*80


if '--panel' in options:
    import vacca.panel
    ret = vacca.panel.main(args[:1]+args[-1:])
    
else:
    confname = 'vaccagui'
    app = TaurusApplication()
    gui = TaurusGui(None, confname=confname)
    gui.show()
    ret = app.exec_()

taurus.info('Finished execution of TaurusGui')
sys.exit(ret)

