
=========================
Overriding VACCA Settings
=========================

Levels
------

There are 4 hierarchic levels of settings in VACCA:

 * The Top Level are the VACCA_* environment variables: VACCA_DIR, VACCA_PATH, VACCA_CONFIG and 
 any VACCA_$ variable where $ matches any of the config variables available in settings file.
 
 * The second level are variables defined in VACCA properties in the TangoDB. These variables can be defined
 as VACCA.{VAR_NAME}:"Value" or as VACCA.{CONFIG}:"VAR_NAME=value". Being {CONFIG} one of the values of 
 VACCA.VaccaConfigs property.
 
 * The third level are the variables defined in the python file passed as argument (or otherwise defined as 
 VACCA_CONFIG or CONFIG_FILE variable).
 
 * Finally, if a setting has no value defined with any of the previous methods; the value is taken from vacca.default
 python module.
 
 Examples
 --------
 
 To launch a vaccagui with a custom synoptic; thus overriding the one specified by default::
 
   VACCA_JDRAW_FILE=BL09/BL09.jdw vaccagui
