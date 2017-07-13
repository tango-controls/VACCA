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
#############################################################################

import fandango,vacca,traceback,taurus
from taurus.qt.qtgui.table.taurusdevicepropertytable import TaurusPropTable

from fandango.qt import DoubleClickable,Dropable
from taurus.external.qt import Qt
from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

try:
    #Taurus 3
    from taurus.core import TaurusDevice,TaurusAttribute,TaurusDatabase as TaurusAuthority
except:
    #Taurus 4
    from taurus.core import TaurusDevice, TaurusAttribute, TaurusAuthority

class VaccaPropTable(DoubleClickable(Dropable(TaurusPropTable))):
    """
    It is a class that inherits from TaurusPropTable, DoubleClickable (fandango) and Dropable (fandango).

    Shows the Devices Properties, this widget is listening to shareDataManager if any Device has been selected to show its properties

    This class has the follow functionalities:
        * Is connected to shareDataManager to share information in the GUI.
        * Can be edit the property by doubleclick function.
    """

    def __init__(self, parent=None, designMode = False):
        """
        In Init, the class VaccaPropTable check if exist any shareDataManager to
        subscribe in it.

        :param parent:
        :param designMode:
        :return:
        """
        #super(type(self),self).__init__(parent,designMode)
        TaurusPropTable.__init__(self,parent,designMode)
        sdm = vacca.utils.get_shared_data_manager()
        if sdm:
            sdm.connectReader('SelectedInstrument',self.setTable,readOnConnect=True)
        print sorted(a for a in dir(self) if 'check'  in a )
        if self.checkDropSupport():
            self.setSupportedMimeTypes([self.TAURUS_DEV_MIME_TYPE,
                                        self.TAURUS_MODEL_MIME_TYPE,
                                        self.TAURUS_MODEL_MIME_TYPE,
                                        self.TAURUS_MODEL_LIST_MIME_TYPE,
                                        self.TEXT_MIME_TYPE])


        self.setAcceptDrops(True)
        #self.setModifiableByUser(True)
        self.setDropEventCallback(self.setTable)
        self.setModelInConfig(False)
        self.setClickHook(self.editProperty)
        
    @staticmethod
    def getPanelDescription(name='TangoDeviceProperties',model=''):
        """
        :param name: Name for the Panel
        :param model: Model for the panel
        :return:
        """
        return PanelDescription(name,classname='vacca.properties.VaccaPropTable',model=model)
    
    def getModelClass(self):
        return TaurusDevice

    def setModel(self,model): 
        """
        Set Model is the callback used in shareDataManager to manage device
        selections.
        :param model:
        :return:
        """
        try:
          self.setTable(model)
        except:
          traceback.print_exc()
        
    def setTable(self,model,filters=[]):
        ''' 
        This method  overrides TaurusPropTable.setTable(), which connects with TaurusClassTable
        This method fill the table with the names of properties and values for the device selected
        '''      
        try:
            model = model and fandango.tango.parse_tango_model(str(model))
            if model is None:
              self.warning('VaccaPropTable.setTable(%s(%s)): MODEL NOT PARSABLE!'%(type(model),model))
              return
            else:
              try: model = model['device']
              except: model = str(model)
              self.debug('VaccaPropTable.setTable(%s(%s))'%(type(model),model))
            
            #TaurusPropTable.setTable(self,model)
            Qt.QObject.disconnect(self,Qt.SIGNAL("cellChanged(int,int)"),self.valueChanged)
            self.db = fandango.get_database()
            dev_name = str(model)
            self.list_prop = list(self.db.get_device_property_list(dev_name,'*'))
            neg = ['polled_attr']+[f[1:] for f in filters if f.startswith('!')]
            pos = [f for f in filters if not f.startswith('!')]
            self.list_prop = [p for p in self.list_prop if
              (not pos or fandango.matchAny(pos,p)) 
              and not fandango.matchAny(neg,p)]
            
            self.setRowCount(len(self.list_prop))
            for i in range(0,len(self.list_prop)):
                elem = self.list_prop[i]
                self.setText(elem,i,0)
                self.dictionary=self.db.get_device_property(dev_name,self.list_prop)
                self.debug('Getting %s properties: %s -> %s'%(dev_name,self.list_prop,self.dictionary))
                value=self.dictionary[elem]
                self.debug('VaccaPropTable: property %s is type %s'%(elem,type(value)))
                USE_TABLES=False
                if USE_TABLES: self.setPropertyValue(value,i,1)
                else:
                    if not isinstance(value,str): #not something like an string
                        #if isinstance(value,list):#type(value) is list: 
                        heigh1 = len(value)
                        value = '\n'.join(str(v) for v in value) # adding new lines in between elements in the list
                    self.setText(str(value),i,1)
            
            self.updateStyle()
            self.dev_name = dev_name
            #self.dev_obj = taurus.Device(dev_name)
            self.setWindowTitle('%s Properties'%dev_name)
            self.resizeColumnsToContents()
            self.resizeRowsToContents()
            
        except:
            traceback.print_exc()
            
    def contextMenuEvent(self,event):
        ''' This function is called when right clicking on qwt plot area. A pop up menu will be
        shown with the available options. '''
        self.info('TaurusPropTable.contextMenuEvent()')
        menu = Qt.QMenu(self)
        configDialogAction = menu.addAction("Add new property")
        self.connect(configDialogAction, Qt.SIGNAL("triggered()"), self.addProperty)
        configDialogAction = menu.addAction("Delete property")
        self.connect(configDialogAction, Qt.SIGNAL("triggered()"), self.deleteProperty)
        configDialogAction = menu.addAction("Edit property")
        self.connect(configDialogAction, Qt.SIGNAL("triggered()"), self.editProperty)
        menu.addSeparator()
        cmd = 'updateDynamicAttributes' if 'DynamicAttributes' in self.list_prop else 'init'
        configDialogAction = menu.addAction("Execute "+cmd+"()")
        self.connect(configDialogAction, Qt.SIGNAL("triggered()"), 
            lambda d=self.dev_name,c=cmd:
              vacca.utils.YesNoDialog('Warning',
              'Are you sure that %s supports %s() command?'%(self.dev_name,c))
              and taurus.Device(d).command_inout(c))
        menu.exec_(event.globalPos())
        del menu    

    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        import vacca.utils
        path = 'image/widgets/Properties.png'
        return vacca.utils.vpath(path)

    @classmethod
    def __test__(klass,arg=None):
        qapp = Qt.QApplication([])
        i = klass()
        print i
        print klass
        i.show()
        if arg: i.setTable(arg)
        qapp.exec_()

__doc__ = vacca.get_autodoc(__name__,vars())

if __name__ == '__main__':
    import sys
    VaccaPropTable.__test__(*sys.argv[1:])
        
