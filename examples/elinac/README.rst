
Execute the ELinac simulation
=============================

PyTango and Taurus must be installed

In addition, get latest fandango and SimulatorDS::

  > git clone https://github.com/tango-controls/fandango fandango.git
  > git clone https://github.com/tango-controls/SimulatorDS
  
Install them using setup.py or just add folders to PATH::

  > export PYTHONPATH=$(pwd):$(pwd)/fandango.git:$PYTHONPATH
  > export PATH=$(pwd)/fandango.git/fandango/scripts:$PATH 

Get Vacca::

  > git clone https://github.com/tango-controls/vacca vacca.git
  > export PATH=$(pwd)/vacca.git/bin:$PATH
  > export PYTHONPATH=$(pwd)/vacca.git:$PYTHONPATH
  > cd vacca.git/examples/elinac

If you don't have the TangoBox devices, create new simulators using SimulatorDS ::

  > ipython
  : import SimulatorDS.gen_simulation as gs
  : gs.generate_class_properties(all_rw=True)
  : gs.create_simulators('ui_attribute_values.pck',instance='elinac',tango_host='127.0.0.1')
  : Ctrl+D

If you have starter, SimulatorDS and fandango/scripts in PATH, let's launch the simulators::

Using Starter and fandango/scripts::

  > tango_servers start "DynamicDS/elinac*"

 Or directly running the .py script::

  > python ../../../fandango.git/fandango/device/DynamicDS.py elinac &

Last, launch VACCA::

  > vaccagui elinac.py

.. image:: screenshot.png

From this point you can select devices from the tree or synoptic, plot values, interact with attributes/commands or start/stop/reload devices and its properties using the right click menus.

If panic and PyTangoArchiving are available, the AlarmGUI and ArchivingBrowser widgets can be added to the perspective for a richer functionality.


Sergi Rubio, 2010 - 2016
