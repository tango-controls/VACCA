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
    --install-lib=lib/python/site-packages --install-scripts=ds

-------------------------------------------------------------------------------
"""

print(__doc__)

version = open('vacca/VERSION').read().strip()
scripts = []
license = 'GPL-3.0'

scripts = ['./bin/vaccagui']

entry_points = {
        'console_scripts': [
            #'CopyCatDS = PyTangoArchiving.interface.CopyCatDS:main',
        ],
}

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

setup(
    name="Vacca",
    version=str(version),
    license=license,
    packages=['vacca'],
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
