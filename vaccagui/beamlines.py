#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
###########################################################################

"""
configuration file for an example of how to specify system-wide defaults for VaccaGUI 

This configuration file determines the default, permanent, pre-defined
options for the GUI; modify them to match your default gui options.

Every CONFIG file loaded by vaccagui will override those options redefined on it; 
use default.py for your common options and whatever.py for your in-place customization.
"""

import fandango,imp

#The device that will be shown by default when loading the application
COMPOSER = DEVICE = fandango.get_matching_devices('BL*/VC/ALL')[0].upper()
DOMAIN = BL = COMPOSER.split('/')[-3]

print '>'*20+' Loading config for beamline %s'%BL

from vacca.utils import WORKING_DIR,wdir,VACCA_PATH,vpath
WDIR = WORKING_DIR

##NOTE: THIS DOESN'T SEEM TO WORK!
EXTRA_APPS = {
    'xtrend':{'name':'NewTrend','classname':'vacca.panel.VaccaAction','model':['Trend',wdir('image/icons/Mambo-icon.png')]+'taurustrend -a'.split()},
    }
    
EXTRA_DEVICES = [
    d for d in (
        fandango.get_matching_devices('*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*')+
        fandango.Astor('PyAlarm/*').get_all_devices())
    if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba'))
    ]
#print 'EXTRA_DEVICES: %s'%EXTRA_DEVICES

GAUGES = [a 
    for d in fandango.get_matching_devices('*/*/(mvc|vgct)*')
    for a in fandango.get_matching_attributes('%s/p[12]'%d)
    if fandango.tango.check_device(d) and str(getattr(fandango.tango.check_attribute(d+'/state'),'value','UNKNOWN')) not in 'UNKNOWN,FAULT'
    ]
    
JDRAW_FILE = wdir('%s/%s.jdw'%(BL,BL))
print 'JDRAW_FILE: %s'%JDRAW_FILE

#Examples of Attribute filters to be applied to DevicePanel
try:
  from config.filters import *
except:
  try:
    from filters import *
    from vacca.filters import *
  except:
    print 'UNABLE TO LOAD filters.py!'

#NOT USED, HAVE A LOOK TO filters.AttributeFilters INSTEAD
def ATTR_FILTER(attr_name):
    attr_name = attr_name.lower()
    if attr_name.endswith('/status'):
        return False
    elif '/all/' in attr_name and any(s in attr_name for s in 
            'axxis,devstates,deviceslist,positions'.split(',')):
        return False
    elif 'vgct' in attr_name:
        if not fandango.matchCl('p[0-9]',attr_name) or 'not used' in attr_name: 
            return False
    return True