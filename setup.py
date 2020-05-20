#!/usr/bin/env python
# Always prefer setuptools over distutils
import os, imp
from setuptools import setup, find_packages

__doc__ = """

To install as system package:

  python setup.py install
  
To install as local package, just run:

  mkdir /tmp/builds/
  python setup.py install --root=/tmp/builds
  /tmp/builds/usr/bin/$DS -? -v4

To tune some options:

  RU=/opt/control
  python setup.py egg_info --egg-base=tmp install --root=$RU/files --no-compile \
    --install-lib=lib/python/site-packages --install-scripts=bin

-------------------------------------------------------------------------------
"""

version = open('vacca/VERSION').read().strip()
scripts = []
license = 'GPL-3.0'

scripts = ['./bin/vaccagui','./bin/vaccapanel','./bin/vaccabar']

entry_points = {
        'console_scripts': [
            #'CopyCatDS = PyTangoArchiving.interface.CopyCatDS:main',
        ],
}
        
package_dir = {'vacca':'vacca'}
package_data = {
    'vacca': [#'VERSION','README',
         'VERSION',
         'CHANGES',
         'image/equips/*',
         'image/icons/*',
         'image/widgets/*',
         'ini/vaccagui/*',
         ]
} 
    
# PARSING EXTRA FILES ADDED TO THE PACKAGE
import os,re

#if os.path.isdir('vaccagui'):
#  print 'Adding custom vaccagui package ...'
#  package_dir['vaccagui'] = 'vaccagui'
#else:
#  package_dir['vaccagui'] = 'vacca/ini/vaccagui'
  
def getter(s,d,files,remove='vaccagui'):
  #d = os.path.join(*(d.split(os.path.sep)[1:] or ['']))
  print d,files
  for n in files:
    n,r = os.path.join(d,n),re.match('.*(pyc|~|git|svn|bak|tmp)$',n)
    if os.path.isfile(n) and not r:
      if n.startswith(remove+os.path.sep):
        n = n.replace(remove+os.path.sep,'')
      s.append(n)

#vg = package_dir['vaccagui']
#package_data['vaccagui'] = []
#os.path.walk(vg,getter,package_data['vaccagui'])
#vgb = os.path.join(vg,'bin')
#if os.path.isdir(vgb):
#  os.path.walk(vgb,
#    lambda l,d,f:l.extend(os.path.join(vgb,n) for n in f),
#    scripts)

import pickle
pickle.dump(package_data,open('data.pck','w'))
  
packages = sorted(set(package_dir.keys()+find_packages()))

setup(
    name="vacca",
    version=str(version),
    license=license,
    packages=packages,
    package_dir=package_dir,
    description="Viewer and Commander Control Application for Tango Control System.",
    long_description="",
    author="Sergi Rubio",
    author_email="srubio@cells.es",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '\
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
    ],
    platforms=[ "Linux" ],
    install_requires=['taurus'],
    scripts=scripts,
    entry_points=entry_points,
    include_package_data=True,
    package_data=package_data,
    zip_safe=False
  )
