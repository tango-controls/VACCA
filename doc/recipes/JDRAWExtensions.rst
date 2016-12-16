Special JDraw Extensions used by SynopticTree
=============================================
 

Classic JDraw Extensions
------------------------
 
::

  className:
  Java class to be launched by this object. If the object is interactive the class will be executed when the ValueChanged is received; if it isn't the class will be executed at MousePressed. If the className is set to "noPanel" nothing is launched.
  classParam:
  first argument to be passed to the java panel e.g, if className is a synopticAppli classParam="asynopticfile.jdw"
  valueList:
  used by *ScalarComboEditor swing objects to acquire the values list used also by atkpanel to read the rest of MainPanel arguments (standAlone, keepStateRrep efresh, propertiesButton, readOnly = "0 1 0 0") for a Combo editor could be "jive xterm mambo" if it asking for an application to launch
  shellCommand:
  It allows to launch any shell command or application (dir, xterm, jive, firefox, etc ...) from the synoptic If a JDObject is interactive and has the shellCommand extension its content will be executed at each valueExceedBounds event The command is always executed in background Streams redirection is not allowed (should be done inside an script) Arguments can be passed to the shell command
  noPrompt:
  If this extension is present external applications are executed w/out prompt
  standAlone:
  If this extension is present external applications are not killed when Synoptic exits
 

Advanced JDraw extensions
-------------------------
 

NOTE: All this extensions are available only if SynopticTree.jar is placed in the Classpath before ATK* packages. When it is done all the extension names become case-independent.

::
  ExtensionsList:
  Extension to introduce as a list in a single field all these extensions that don't require a value (Boolean). These extensions have no value but any call to obj.hasExtendedParam(Extension) returns a TRUE value. It simplifies the declaration of extensions.

Graphic Extensions
------------------
 
::

  tangoColors:
  ATK JDraw deprecates standard Tango-State Colors if any option is enabled in the interactivity panel. This extension has been added to force JDraw to apply the original TangoColors to this object
  noTooltip:
  To not generate a tooltip for an object.
  ignoreRepaint:
  Color changes (e.g. due to state) are not propagated through this device It was previously implemented by setting "IgnoreRepaint" as object's name
 
Events propagation Extensions
-----------------------------
 
::

  isContainer:
  Groups already mouseified (assigned to devices, attributes or commands) will be recursively parsed only if the have this extension; if it isn't internal objects will be ignored.
  ignoreMouse:
  This object will ignore any mouse event (e.g. MousePressed); but it will continue reacting to group-managed events if they are configured.
  eventReceivers:
  If a single Object's interactivity must affect other objects (e.g change of visibility of an specific set of objects, like pressure values), its names (separated by commas) must be listed here. It could be a regular expression matching the object names.
  groupHook:
  Extension to mark an object as the receiver or executer of all the mouse events on a JDraw Group. The object can be part of the group or not and the value of the string will vary the propagation of the event.


  groupHook="":
  When the object is part of a group it receives and executes all the events in the group; but these are not propagated to the rest of devices in the group. Rest of devices in the group continue having its own events if they don't have the ignoreMouse extension.

SynopticTree specific Extensions
--------------------------------
 
::

  isSynoptic:
  Mark an object to be added as a new SynopticTree branch, read its internal list of devices and create a new Synoptic panel for it.
  xmlFile:
  Profile with the attributes to be displayed in the Attribute and Trend panels when this synoptic file is loaded. This extension must be set for a single object in the jdw file (the background or title objects by convention).
