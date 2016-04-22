#!/usr/bin/env python

"""
configuration file for an example of how to specify system-wide defaults for VaccaGUI 

This configuration file determines the default, permanent, pre-defined
options for the GUI; modify them to match your default gui options.

Every CONFIG file loaded by vaccagui will override those options redefined on it; 
use default.py for your common options and whatever.py for your in-place customization.
"""

import fandango,imp,re

#The device that will be shown by default when loading the application
COMPOSER = DEVICE = 'I/VAC/ALL'
DOMAIN = BL = COMPOSER.split('/')[-3]

print '>'*20+' Loading config for beamline %s'%BL

from vacca.utils import wdir

##NOTE: THIS DOESN'T SEEM TO WORK!
EXTRA_APPS = {
    'xtrend':{'name':'NewTrend','classname':'vacca.panel.VaccaAction','model':['Trend',wdir('image/icons/Mambo-icon.png')]+'taurustrend -a'.split()},
    }

get_ordinal = lambda s: (fandango.str2int(s) if re.search('[0-9]',s) else None)
#section0 = [d for d in fandango.get_matching_devices('*/vac/*') if get_ordinal(d) in (None,0,1)]
folder = '/home/sicilia/Projects/VaccaMAX/'
section0 = open(folder+'devices.csv').read().split()
plcs = map(str.lower,('I-K02/VAC/PLC-01-VALV','i-k02/vac/plc-01-ipcu','i-k02/vac/plc-01',))
vcdevs = map(str.lower,['I/VAC/ALL']+section0+fandango.get_matching_devices('i/pss/*')+plcs)
vcdevs += [d.replace('k0','s0') for d in vcdevs if 'ipcua' in d.lower()] # and fandango.check_device(d.replace('k0','s0'))]
    
EXTRA_DEVICES = [v for v in vcdevs if any(s in v.lower() for s in ('vac','plc','alarm'))]#[d for d in vcdevs if fandango.check_device(d)]
print 'EXTRA_DEVICES: [%d]'%len(EXTRA_DEVICES)

    #d for d in (
        #fandango.get_matching_devices('*(pnv|eps|vfcs|ccg|mvc|pir|elotech|bestec|/hc-|/ip-|rga|ipct|vgct|bakeout|tsp|cry|fcv|fs-|otr|vc/all|alarm)*')+
        #fandango.Astor('PyAlarm/*').get_all_devices())
    #if not any(s in d.lower() for s in ('dserver','mbus','serial','ccd','iba'))
    
#print 'EXTRA_DEVICES: %s'%EXTRA_DEVICES

GAUGES = []
    #a 
    #for d in fandango.get_matching_devices('*/*/(mvc|vgct)*')
    #for a in fandango.get_matching_attributes('%s/p[12]'%d)
    #if fandango.tango.check_device(d) and str(getattr(fandango.tango.check_attribute(d+'/state'),'value','UNKNOWN')) not in 'UNKNOWN,FAULT'
    #]
    
#JDRAW_FILE = imp.find_module('vacca')[1]+'/%s/%s.jdw'%(BL,BL)
#JDRAW_FILE = folder+'linac/images/maxiv.org.svg'
JDRAW_FILE = '/home/sicilia/Projects/VaccaMAX/linac/images/maxiv.svg'
print 'JDRAW_FILE: %s'%JDRAW_FILE

