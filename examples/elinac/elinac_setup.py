"""
Script to create the devices needed for the ELINAC simulation

Dependencies are fandango, PyTango, PySignalSimulator

srubio, 2012
"""

import pickle
import fandango as fn

properties = fn.defaultdict(list)

devattrs = pickle.load(open('ui_attribute_values.pck'))

for dev,values in devattrs.items():
  pass

