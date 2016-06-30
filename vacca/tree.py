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

__all__ = ["TaurusDevTree","TaurusSearchTree","TaurusDevTreeOptions","VaccaTree"] #,"SearchEdit"] #"TaurusTreeNode"]

import time,os,re,traceback
from functools import partial
import fandango,PyTango

try:import icons_dev_tree
except:icons_dev_tree = None

from taurus.external.qt import Qt

import taurus.core
from taurus.core.util.colors import DEVICE_STATE_PALETTE,ATTRIBUTE_QUALITY_PALETTE
from taurus.core.util.containers import CaselessDict
from taurus.core.tango.search import * #@TODO: Avoid implicit imports
from taurus.qt.qtcore.util.emitter import SingletonWorker
from taurus.qt.qtcore.mimetypes import *  #@TODO: Avoid implicit imports
from taurus.qt.qtcore.util import properties
from taurus.qt.qtcore.util.properties import djoin
from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget
from taurus.qt.qtgui.container import TaurusWidget

TREE_ITEM_MIME_TYPE = 'application/x-qabstractitemmodeldatalist'
import taurus.qt.qtgui.tree.taurusdevicetree
from taurus.qt.qtgui.tree.taurusdevicetree import *
from taurus.qt.qtcore.mimetypes import *


#TaurusDevTree.setDefaultPanelClass is setting the widget to open when ContextMenu->OpenPanel is selected
TaurusSearchTree.setDefaultPanelClass = staticmethod(lambda c: TaurusDevTree.setDefaultPanelClass(c))
#TaurusDevTree.setDefaultPanelClass is setting the attributes to show when ContextMenu->ShowAttributes is selected
TaurusSearchTree.setDefaultAttrFilter = staticmethod(lambda c: TaurusDevTree.setDefaultAttrFilter(c))

class VaccaDevTree(taurus.qt.qtgui.tree.taurusdevicetree.TaurusDevTree,TaurusBaseWidget):
    
    ## @TODO: SAME CHANGE MUST BE ADDED TO TAURUSJDRAWGRAPHICS SELECTGRAPHICITEM!!!
    
    def trace(self,msg):
        if self.TRACE_ALL or self.getLogLevel() in ('DEBUG',40,):
            print 'TaurusDevTree.%s: %s'%(self.getLogLevel(),msg[:80]+'...') #@TODO: use the taurus logger instead! ~~cpascual 20121121    
    
    def findInTree(self,*a,**k):
        try:
            #Added to avoid recursion
            print('VaccaDevTree.findInTree(%s,%s)' % (a, k))
            if self.currentItem() and str(
                    self.getNodeDraggable()).lower().strip() == \
                    str(k.get('regexp', a[0])).lower().strip():
                return
            TaurusDevTree.findInTree(self, *a, **k)
        except:
            print traceback.format_exc()
            
    def getModelMimeData(self):
        '''Returns a MimeData object containing the model data. The default implementation 
        fills the `TAURUS_MODEL_MIME_TYPE`. If the widget's Model class is
        Attribute or Device, it also fills `TAURUS_ATTR_MIME_TYPE` or
        `TAURUS_DEV_MIME_TYPE`, respectively
        '''
        mimeData = Qt.QMimeData()
        node = self.currentItem() 
        draggable = self.getNodeDraggable(node)
        if draggable:
            slashes = draggable.count('/')-draggable.count(':')
            #Set 'Text' To be compatible with other Widgets 'Text/plan':
            mimeData.setText(draggable)
            if slashes==3: mimeData.setData(TAURUS_ATTR_MIME_TYPE, draggable)
            elif slashes==2: 
                mimeData.setData(TAURUS_DEV_MIME_TYPE, draggable)
                print 'mimeData is %s,%s'%(TAURUS_DEV_MIME_TYPE, draggable)
            elif slashes: mimeData.setData(TAURUS_MODEL_MIME_TYPE, draggable)
        print mimeData
        print map(str,mimeData.formats())
        return mimeData            
    
    def setNodeTree(self,parent,diction,alias=False):
        """ OVERRIDEN TO ADD try/except CATCHES
        It has parent as argument to allow itself to be recursive
        Initializes the node tree from a dictionary {'Node0.0':{'Node1.0':None,'Node1.1':None}}
        """
        self.debug('In setNodeTree(%d,alias=%s) ...'%(len(diction),alias))
        if not hasattr(diction,'keys'): diction = dict.fromkeys(diction)
        for node in sorted(diction.keys()):
            assert int(self.index)<10000000000,'TooManyIterations!'
            try:
                self.index = self.index + 1
                dev_alias = alias and str(node).count('/')==2 and get_alias_for_device(node)
                text = '%s (%s)'%(node,dev_alias) if dev_alias else node
                if diction[node] and any(diction[node]):
                    item = self.createItem(parent,node,text)
                    self.setNodeTree(item,diction[node],alias)
                else:
                    item = self.createItem(parent,node,text)
            except:
                self.warning('setNodeTree(%s,%s) failed!: %s'%(parent,node,traceback.format_exc()))
    
    
class VaccaTree(TaurusSearchTree):
    """
    It is a class that inherits from TaurusSearchTree.
    Allow show the devices and start/stop it with the right button (
    expandable menu)

    """
    
    
    # This slots are overloaded here because they are not yet in the last taurus package. Once it will be included in TaurusSearchTree than it can be removed.
    # The slots are needed because the method_forwarder method is not seen from the SharedDataManager side.
    
    #def __getattr__(self,attr):
        #if attr!='tree': 
          #return getattr(self.tree,attr)

    ## DO  NOT REMOVE YET!!
    def setTangoHost(self,*a,**k): self.tree.setTangoHost(*a,**k)
    def addModels(self,*a,**k):  self.tree.addModels(*a,**k)
    def setModel(self,*a,**k):  self.tree.setModel(*a,**k)
    def setModelCheck(self,*a,**k):  self.tree.setModelCheck(*a,**k)
    def setTree(self,*a,**k):  self.tree.setTree(*a,**k)
    def expandAll(self,*a,**k):  self.tree.expandAll(*a,**k)
    def loadTree(self,*a,**k):  
        print('VaccaTree.loadTree(...)')
        self.tree.loadTree(*a,**k)
            
    @staticmethod
    def setDefaultPanelClass(*a, **k):
        TaurusDevTree.setDefaultPanelClass(*a, **k)

    @staticmethod
    def setDefaultAttrFilter(*a, **k):
        TaurusDevTree.setDefaultAttrFilter(*a, **k)

    @classmethod
    def setIconMap(klass, iconMap):
        TaurusDevTree.setIconMap(iconMap)
    
    def start_server(self, device=None):
        """
        Allow start Servers.
        :param device: DeviceName
        :return:
        """
        device = device or self.tree.getNodeDeviceName()
        self.astor.load_by_name(device)
        ss = self.astor.get_device_server(device)
        text, ok = Qt.QInputDialog.getText(self, 'Start Server','Start %s at '
                                                               'host ...'
                                           % ss, Qt.QLineEdit.Normal,
                                           self.astor[ss].host)
        if ok:
            return self.astor.start_servers(ss, host=str(text))
        else:
            return False
        
    def stop_server(self, device=None):
        """
        Allow stop Servers
        :param device: DeviceName
        :return:
        """
        device = device or self.tree.getNodeDeviceName()
        self.astor.load_by_name(device)
        ss = self.astor.get_device_server(device)
        v = Qt.QMessageBox.warning(self, 'Stop Server', '%s will be killed!, '
                                                       'Are you sure?',
                                   Qt.QMessageBox.Yes|Qt.QMessageBox.No)
        if v == Qt.QMessageBox.Yes:
            return self.astor.stop_servers(ss)
        else:
            return False
        
    def device_info(self,device=None):
        """
        Show a the Device Info
        :param device: DeviceName
        :return:
        """
        device = device or self.tree.getNodeDeviceName()
        di = fandango.tango.get_device_info(device)
        txt = '\n'.join('%s : %s'%(k,getattr(di,k)) for k in 'name dev_class server host level exported started stopped PID'.split())
        v = Qt.QMessageBox.information(self,device,txt,Qt.QMessageBox.Ok)
        
    def defineStyle(self):
        #print('In TaurusSearchTree.defineStyle()')
        self.setWindowTitle('VaccaTree')
        self.setLayout(Qt.QVBoxLayout())
        self.edit = TaurusDevTreeOptions(self)
        self.tree = VaccaDevTree(self)
        self.astor = fandango.Astor()
        if 'Start Server' not in dict(self.tree.ExpertMenu):
            self.tree.ExpertMenu.append(('Start Server', self.start_server))
            self.tree.ExpertMenu.append(('Stop Server', self.stop_server))
            self.tree.ExpertMenu.append(('Device Info', self.device_info))
        self.layout().addWidget(self.edit)
        self.layout().addWidget(self.tree)
        self.registerConfigDelegate(self.tree)
        #Event forwarding ...
        for signal in TaurusDevTree.__pyqtSignals__:
            Qt.QObject.connect(self.tree,
                               Qt.SIGNAL(signal),
                               lambda args,
                                      f = self,
                                      s = signal: f.emit(Qt.SIGNAL(s), args))
        self.edit.connectWithTree(self.tree)
        return    

    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        path = 'image/widgets/Tree.png'
        return path

from .doc import get_autodoc
__doc__ = get_autodoc(__name__,vars())

###############################################################################

