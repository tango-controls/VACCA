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

import fandango,vacca,traceback
from taurus.qt.qtgui.table.taurusdevicepropertytable import TaurusPropTable

from fandango.qt import DoubleClickable,Dropable
from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE
from taurus.core import TaurusDevice,TaurusAttribute,TaurusDatabase
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

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
        return PanelDescription(name,'vacca.properties.VaccaPropTable',model)
    
    def getModelClass(self):
        return TaurusDevice

    def setModel(self,model): 
        """
        Set Model is the callback used in shareDataManager to manage device
        selections.
        :param model:
        :return:
        """
        model = fandango.tango.parse_tango_model(str(model))['device']
        self.setTable(model)
        
    def setTable(self,model):
        try:
            model = fandango.tango.parse_tango_model(str(model))['device']
            print('VaccaPropTable.setTable(%s(%s))'%(type(model),model))
            TaurusPropTable.setTable(self,model)
        except:
            traceback.print_exc()

    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        path = 'image/widgets/Properties.png'
        return path

    @classmethod
    def __test__(klass,arg=None):
        from PyQt4 import Qt
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
        
