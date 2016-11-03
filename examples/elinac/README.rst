
# Execute the ELinac simulation
# =============================

# PyTango and Taurus must be installed

# In addition, get latest fandango and SimulatorDS

> git clone https://github.com/tango-controls/fandango
> git clone https://github.com/tango-controls/SimulatorDS

# Get Vacca

> git clone https://github.com/sergirubio/vacca vacca.git
> cd vacca.git/examples/elinac

# Create the simulators

> ipython
: import Simulator.gen_simulation as gs
: gs.generate_class_properties()
: gs.create_simulators('ui_attribute_values.pck',instance='elinac',tango_host='127.0.0.1')
: Ctrl+D

# If you have starter and fandango/scripts in PATH, let's launch the simulators:

> tango_servers start "SimulatorDS/elin*"

# Last, launch VACCA

> vaccagui elinac.py

# Enjoy

# srubio, 2010 - 2016
