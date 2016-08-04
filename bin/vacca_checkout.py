#!/usr/bin/env python

# @file: vacca/installer.py

import os,sys,argparse,imp

VACCA_URL = 'https://svn.code.sf.net/p/tango-cs/code/tools/vacca/trunk'

ACTIONS = 'get','download','check','update','reset','cleanup'

MODULES = ['bin','vacca','vaccagui','doc','README']

DEVICES = ['PyPLC', 'PyAlarm', 'PyStateComposer', 'PySignalSimulator', 'DataBaseDS']

PACKAGES = [
  ('vacca', #It will be the only module installed in root folder, all the rest will use subdirectories
    'svn co '+VACCA_URL+' .'),
  ('fandango',
    'git clone https://github.com/sergirubio/fandango.git fandango.git; ln -s fandango.git/fandango'),
    #'svn co https://svn.code.sf.net/p/tango-cs/code/share/fandango/trunk/fandango'),
  ('PySignalSimulator',
    'svn co https://svn.code.sf.net/p/tango-ds/code/DeviceClasses/Simulators/PySignalSimulator/trunk PySignalSimulator'),
  #('DataBaseDS',
    #'svn co https://svn.code.sf.net/p/tango-ds/code/DeviceClasses/Simulators/PySignalSimulator/branches/DataBaseDS/databaseds.8.1.6 DataBaseDS'),
  ('panic',
   # 'ln -s PyAlarm/panic'),  
   'git clone https://github.com/sergirubio/panic.git panic.git ; ln -s panic.git/panic'),
  ('PyAlarm',
    #'svn co https://svn.code.sf.net/p/tango-ds/code/DeviceClasses/SoftwareSystem/PyAlarm/trunk PyAlarm'),
    'ln -s panic/ds PyAlarm'),
  ('panic-gui',
    #'svn co https://svn.code.sf.net/p/tango-ds/code/Clients/python/Panic/trunk panic/gui; ln -s panic/gui panic-gui'),
    'ln -s panic/gui panic-gui'),
  ('PyTangoArchiving',
    'svn co https://svn.code.sf.net/p/tango-cs/code/archiving/tool/PyTangoArchiving/trunk PyTangoArchiving.svn ; ln -s PyTangoArchiving.svn/PyTangoArchiving'),
  #('PyStateComposer',
    #'svn co https://svn.code.sf.net/p/tango-ds/code/DeviceClasses/Calculation/PyStateComposer/trunk/src PyStateComposer'),
  #('PyPLC',
    #'svn co https://svn.code.sf.net/p/tango-ds/code/DeviceClasses/InputOutput/PyPLC/trunk PyPLC'),
  ('taurus',
    'echo "TAURUS NOT INSTALLED BY VACCA, GET IT FROM https://pypi.python.org/pypi/taurus"'),
  ]
  
def check_repo(folder):
    repo = 'svn' if os.path.isdir(folder+'/.svn') else 'git' if os.path.isdir(folder+'/.git') else ''
    if repo:
      os.system('cd %s; %s status'%(folder,repo))

def check_package(package,prefix='',trace=True):
    #print('in vacca.setup.check_package(%s,%s)'%(package,prefix))
    type_ = ''
    try:
      #Trying raw installation:
      if os.path.isdir(package):
        if trace: print('INFO: Package %s installed at %s.'%(package,prefix))
        check_repo(package if package!='vacca' else prefix)
        return 1      
      #Trying pythonpath:
      folder = imp.find_module(package)[1]
      prefix = prefix or os.getcwd()
      if prefix and prefix not in os.path.abspath(folder):
        if trace: print('WARNING: Package %s not installed within VACCA, but available from PYTHONPATH'%package)
        return -1 
      else:
        if trace: print('INFO: Package %s installed at %s'%(package,folder))
        check_repo(folder if package!='vacca' else prefix)
        return 1
    except:
      #traceback.print_exc()
      if trace: print('ERROR: Package %s not installed nor available, some VACCA widgets may not work'%package)  
      return 0
  
def install(prefix,package=''):

  print('Installing Vacca dependencies (%s) at:  %s'%(package,prefix))
  os.chdir(prefix)
  packages = [t for t in PACKAGES if check_package(t[0],trace=0)!=1 and (not package or t[0]==package)]
  
  if not packages:
    print('All packages already installed, exiting ...')
    return
  
  print('The following packages will be installed : %s'%','.join(t[0] for t in packages))
  
  packs = raw_input('Do you want to continue? (Y/n/!package)')
  if packs.lower().startswith('n'):
    return
    
  for package,command in packages:
    
    if packs.startswith('!') and package in packs:
      print('\n'+'Skipping %s ...'%package)
      continue
      
    print('\n'+'#'*80+'\nGetting %s\n'%package + '\n')
    
    if os.path.isdir(package):
      if os.path.isfile(package):
        print('ERROR: A file called %s prevents package from installing!'%package)
        break
      else:
        print('WARNING: Package %s already installed, skipping ...'%package)
        continue
        
    print(command)
    os.system(command)

    check_package(package,prefix)
    
  if not os.path.isfile(prefix+'/bin/vaccagui.sh'):
    launcher = prefix+'/bin/vaccagui.sh'
    f = open(launcher,'w')
    f.write(open(prefix+'/bin/vaccagui').read().replace('#source alba_blissrc','VACCA_PATH='+prefix))
    f.close()
    os.system('chmod +x '+launcher)
        
  print('\nInstallation at %s finished'%prefix)
  
def update(prefix,package=''):

  print('Updating Vacca dependencies (%s) at:  %s'%(package,prefix))
  os.chdir(prefix)
  
  packages = [t for t in PACKAGES if check_package(t[0],trace=0)==1 and (not package or t[0]==package)]
  
  if not packages:
    print('... packages not installed, exiting ...')
    return
  
  print('The following packages will be updated : %s'%','.join(t[0] for t in packages))

  if raw_input('Do you want to continue? (Y/n)').lower().startswith('n'):
    return
    
  for package,command in packages:
    
    print('\n'+'#'*80+'\nUpdating %s\n'%package + '\n')
    
    if os.path.isdir(package):
      if os.path.isfile(package):
        print('ERROR: A file called %s prevents package from installing!'%package)
        break
      else:
       if package!='vacca': #vacca installed in root folder
          os.chdir(package)
       command = 'svn update --force' if 'svn' in command else ('git fetch; git pull' if 'git' in command else '')
       print(command)
       os.system(command)
    else: 
      print('not found!!!?')
    os.chdir(prefix)
    check_package(package,prefix)
        
  print('\nUpdate at %s finished'%prefix)  
    
def cleanup(prefix):
  
  print('Cleanup of %s ...'%prefix)
  os.chdir(prefix)
  files = [f for f in ([t[0] for t in PACKAGES]+
            ['.git','.svn','CVS','*pyc','*py~']+
            ['bin','doc','README','vaccagui']) 
          if os.path.isfile(f) or os.path.isdir(f) or '*' in f]

  for f in files:
    f = prefix+'/'+f
    print('Removing %s ...'%f)
    q = (raw_input('Are you sure? (Y/n)').lower() or 'n')[0]
    if q in 'y':
      os.system('rm -rf %s'%f)
  return

def reset_config(confirm=''):
    print('')
    print('Previous Vacca configs:')
    os.system('echo "$(ls ~/.config/VACCA/*.ini)"')
    if not confirm:
        confirm = raw_input('To avoid bugs all the previous VACCA configs need to be removed. Ok? (y/n)?').lower()
    if confirm.startswith('y'):
        print('Removing previous taurus .ini files in ~/.config/VACCA/')
        os.system('rm -v ~/.config/VACCA/*.ini')
    print('')

def main(args):
  current,module = os.getcwd(),os.path.dirname(os.path.abspath(__file__))
  #A non-module folder can be the root for vacca_checkout.py
  prefix = current if current!=module or not os.path.isfile('config.py') else os.path.split(module)[0] 
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw',help='skip svn resync',nargs='?',const=True,default=False,required=False)
  parser.add_argument('--prefix',help='prefix, what else?',default=prefix,required=False)
  parser.add_argument('action',help='|'.join(ACTIONS),metavar='|'.join(ACTIONS),default='get')
  parser.add_argument('--package',help='<package to get, all if not specified>',default='')
  opts = parser.parse_args(args)
  prefix = os.path.abspath(opts.prefix)
  print(prefix+'/bin/vacca_checkout.py %s\n'%' '.join(args))
  
  if not opts.raw:

    q = raw_input('Before continuing, Do you want to update vacca_checkout script from repository? (y/n)?').lower()
    if q.startswith('y'):
      print('Updating setup.py script from SVN repository (use --raw to skip this check)')
      os.system('svn export --force %s/bin/vacca_checkout.py'%VACCA_URL)
      setup = imp.load_source('setup','vacca_checkout.py')
    else:
      setup = imp.load_source('setup',__file__)
      
    print('\n\nContinuing setup at %s ...'%prefix)
    setup.main(list(args)+['--raw'])

  else:
    
    if opts.action in ('get','download'): 
        reset_config()
        install(prefix,opts.package)
    if opts.action in ('update'): 
        reset_config()
        update(prefix,opts.package)
    if opts.action in ('reset',): 
        reset_config('y')
    if opts.action=='cleanup': 
        reset_config()
        cleanup(prefix)
    if opts.action=='check': 
      if opts.package: 
        check_package(opts.package)
      else:
        [check_package(p[0]) for p in PACKAGES]
      
    os.chdir(current)

try:
  import vacca.doc as doc
  __doc__ = doc.get_autodoc(__name__,vars())
except:
  pass
   
if __name__ == '__main__':
  main(sys.argv[1:])


