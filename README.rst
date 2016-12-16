=====
VACCA
=====

DESCRIPTION
===========

VACCA is a versatile Control System Navigator tool built on top of the Taurus framework.
It was developed by Sergi Rubio (srubio@cells.es) as the VACuum Control Application for ALBA Synchrotron.

https://github.com/tango-controls/VACCA

It provides:

 * Enhanced control system navigation, interactive browsing between synoptic, device tree, panels and device searching tools.
 * A customizable interface, allowing user groups to have different views and configure and save their own perspectives.
 * Control over tango devices and other tango services like Archiving, Astor/Starter or Tango DB properties.
 * Filters at Device/Attribute/Command level, to display only the devices/attributes users are interested in.

Since Vacca 2.0 the application is build on top of taurus-gui. Its default setup includes 4 initial perspectives combining tree, synoptic, device panel, attribute grids, taurus trends and some common vacuum panels like pressure/temperature profiles.

.. image:: doc/vacca_screenshot.png

LINKS / DEPENDENCIES
====================

All dependencies and User Manual are available from www.tango-controls.org:

Tango
PyTango
Taurus
Fandango

INSTALLING:
===========

Copy vacca folder to a folder in your PYTHONPATH
Copy ./vaccagui script to a folder in your PATH
Copy default.py.ini to default.py and edit your default options (follow comments in the file)

For a fast way to test VACCA, try the ELINAC example:

 * https://github.com/sergirubio/VACCA/blob/master/examples/elinac/README.rst

CONTENTS:
=========

 * bin/vaccagui : a launcher script
 * vaccagui : an application definition for taurusgui

  * vaccagui.__init__ : it loads the contents of vacca.config module
  * vaccagui/default.ini : 4 perspectives by default (from showing all widgets to minimal for small screens)

 * vacca : the main module

CUSTOMIZING:
============

The idea is to have general config in default.py (ORGANIZATION_LOGO, EXTRA_APPS, ...) and use another file to customize to your beamline/system.
Copy default.py to my_beamline.py; modify variables like JDRAW_FILE, COMPOSER, GRID, DEVICE, GAUGES, ...
Remove all variables you don't need to modify (if ORGANIZATION_LOG is the same for all do not have it declared in many files)

RUNNING:
========

Launch the gui as:
 ./vaccagui path/to/mybeamline.py 

Path to your file must be absolute or relative from "vacca" module location.
If no config file is passed as argument the application will try to open $TANGO_HOST.py if exists (lazy deployment).

----

Creating a new default.ini:

To create a new default file for QSettings you have to remember that models must be clean up for Tree, Gauges and Profile widgets; if not the default file will not behave properly.
