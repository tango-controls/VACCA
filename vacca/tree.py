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
from PyQt4 import QtCore

__all__ = ["TaurusDevTree", "TaurusSearchTree", "TaurusDevTreeOptions",
           "VaccaTree"]  # ,"SearchEdit"] #"TaurusTreeNode"]

import time, traceback
import fandango

try:
    import icons_dev_tree
except ImportError:
    icons_dev_tree = None

from taurus.external.qt import Qt

import taurus.core
from taurus.core.util.colors import DEVICE_STATE_PALETTE

from taurus.core.tango.search import get_alias_for_device
from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget

TREE_ITEM_MIME_TYPE = 'application/x-qabstractitemmodeldatalist'
import taurus.qt.qtgui.tree.taurusdevicetree
from taurus.qt.qtgui.tree.taurusdevicetree import *
from taurus.qt.qtcore.mimetypes import *

# TaurusDevTree.setDefaultPanelClass is setting the widget to open when ContextMenu->OpenPanel is selected
TaurusSearchTree.setDefaultPanelClass = staticmethod(lambda c: TaurusDevTree.setDefaultPanelClass(c))
# TaurusDevTree.setDefaultPanelClass is setting the attributes to show when ContextMenu->ShowAttributes is selected
TaurusSearchTree.setDefaultAttrFilter = staticmethod(lambda c: TaurusDevTree.setDefaultAttrFilter(c))


class VaccaDevTree(taurus.qt.qtgui.tree.taurusdevicetree.TaurusDevTree, TaurusBaseWidget):
    ## @TODO: SAME CHANGE MUST BE ADDED TO TAURUSJDRAWGRAPHICS SELECTGRAPHICITEM!!!

    def trace(self, msg):
        if self.TRACE_ALL or self.getLogLevel() in ('DEBUG', 40,):
            print 'TaurusDevTree.%s: %s' % (
            self.getLogLevel(), msg[:80] + '...')  # @TODO: use the taurus logger instead! ~~cpascual 20121121

    def findInTree(self, *a, **k):
        try:
            # Added to avoid recursion
            print('VaccaDevTree.findInTree(%s,%s)' % (a, k))
            if self.currentItem() and str(
                    self.getNodeDraggable()).lower().strip() == \
                    str(k.get('regexp', a[0])).lower().strip():
                return
            TaurusDevTree.findInTree(self, *a, **k)
        except:
            print traceback.format_exc()

    def getModelMimeData(self):
        """ Returns a MimeData object containing the model data. The default implementation
        fills the `TAURUS_MODEL_MIME_TYPE`. If the widget's Model class is
        Attribute or Device, it also fills `TAURUS_ATTR_MIME_TYPE` or
        `TAURUS_DEV_MIME_TYPE`, respectively
        """
        mimeData = Qt.QMimeData()
        node = self.currentItem()
        draggable = self.getNodeDraggable(node)
        if draggable:
            slashes = draggable.count('/') - draggable.count(':')
            # Set 'Text' To be compatible with other Widgets 'Text/plan':
            mimeData.setText(draggable)
            if slashes == 3:
                mimeData.setData(TAURUS_ATTR_MIME_TYPE, draggable)
            elif slashes == 2:
                mimeData.setData(TAURUS_DEV_MIME_TYPE, draggable)
                print 'mimeData is %s,%s' % (TAURUS_DEV_MIME_TYPE, draggable)
            elif slashes:
                mimeData.setData(TAURUS_MODEL_MIME_TYPE, draggable)
        print mimeData
        print map(str, mimeData.formats())
        return mimeData

    def setNodeTree(self, parent, diction, alias=False):
        """ OVERRIDEN TO ADD try/except CATCHES
        It has parent as argument to allow itself to be recursive
        Initializes the node tree from a dictionary {'Node0.0':{'Node1.0':None,'Node1.1':None}}
        """
        self.debug('In setNodeTree(%d,alias=%s) ...' % (len(diction), alias))
        if not hasattr(diction, 'keys'): diction = dict.fromkeys(diction)
        for node in sorted(diction.keys()):
            assert int(self.index) < 10000000000, 'TooManyIterations!'
            try:
                self.index = self.index + 1
                dev_alias = alias and str(node).count('/') == 2 and get_alias_for_device(node)
                text = '%s (%s)' % (node, dev_alias) if dev_alias else node
                if diction[node] and any(diction[node]):
                    item = self.createItem(parent, node, text)
                    self.setNodeTree(item, diction[node], alias)
                else:
                    item = self.createItem(parent, node, text)
            except:
                self.warning('setNodeTree(%s,%s) failed!: %s' % (parent, node, traceback.format_exc()))

    def getAllNodes(self):
        """ Returns a list with all node objects. """
        return self.item_index
      
    ###########################################################################
    # Update node colors
      
    def setIcons(self,dct={},root_name=None,regexps=True):
        '''
        This method change the icons depending of the status of the devices
        Dict is a dictionary with name of device and colors such as 
        {name_device:color,name_device2:color2}
        An alternative may be an icon name!
        '''
        try:
          state2color = lambda state: Qt.QColor(DEVICE_STATE_PALETTE.number(state))
          self.node_colors = getattr(self,'node_colors',{})
          dct = dict((k,v) for k,v in dct.items() if v!=self.node_colors.get(k,None))

          def update_node(node,key,dct):
              if hasattr(node,'CustomForeground'):
                  node.setForeground(0,Qt.QBrush(Qt.QColor(node.CustomForeground)))
              if hasattr(node,'CustomBackground'):
                  node.setBackground(0,Qt.QBrush(Qt.QColor(node.CustomBackground)))            
              elif hasattr(node,'StateBackground'):
                  node.setBackground(0,Qt.QBrush(state2color(dct[key])))
              if hasattr(node,'CustomIcon'):
                  node.setIcon(0,Qt.QIcon(node.CustomIcon))
              else:
                  if key.count('/')==2:
                      self.setStateIcon(node,dct and dct[key] or '')
              return

          nodes = self.getAllNodes()
          
          for name,node in nodes.iteritems():
              name = str(name).split()[0]
              if node.isHidden(): continue
              if regexps:
                  matches = [v for k,v in dct.items() if re.match(k.lower(),name.lower())]
                  if matches: 
                      update_node(node,name,{name:matches[0]})
              elif name in dct:
                  update_node(node,name,dct or {name:''})
                  
          self.node_colors.update(dct)
        except:
          self.warning('setIcons(): \n%s'%traceback.format_exc())
    
    def setStateIcon(self, child, color):
        color_codes = {
            '#00ff00,ON,OPEN,EXTRACT': ':/ICON_GREEN',
            "#ff0000,OFF,FAULT": ":/ICON_RED",
            "#ff8c00,ALARM": ":/ICON_ORANGE",
            "#ffffff,CLOSE,INSERT": ":/ICON_WHITE",
            "#80a0ff,MOVING,RUNNING": ":/ICON_BLUE",
            "#ffff00,STANDBY": ":/ICON_YELLOW",
            "#cccc7a,INIT": ":/ICON_BRAWN",
            "#ff00ff,DISABLE": ":/ICON_PINK",
            "#808080f,None,UNKNOWN": ":/ICON_GREY",
        }
        if icons_dev_tree is None:
            self.debug('In setStateIcon(%s,%s): Icons for states not available!'%(child,color))
            self.setStateBackground(child,color)
        else:
            icon = ":/ICON_WHITE"
            for states, code in color_codes.items():
                if str(color).upper() in states.upper():
                    icon = code
            self.debug('setStateIcon(%s) => %s' % (color, icon))
            icon = Qt.QIcon(icon)
            child.setIcon(0, icon)

    def setStateBackground(self, child, color):
        if not isinstance(color, Qt.QColor):
            if DEVICE_STATE_PALETTE.has(color):
                qc = Qt.QColor(*DEVICE_STATE_PALETTE.rgb(color))
            else:
                qc = Qt.QColor(color) if not fandango.isSequence(color) else Qt.QColor(*color)
        child.setBackground(0, Qt.QBrush(qc))

    def showNodeContextMenu(self,node,event):
        """
        A pop up menu will be shown with the available options. 
        Menus are managed using two tuple lists for each node: node.ContextMenu and node.ExpertMenu
        """
        obj = self.getNodeDraggable(node)
        position = event.globalPos()
        self.debug('showNodeContextMenu(%s)'%obj)
        if self.itemAt(position) is self.headerItem():
            node = self.headerItem()
            #node.ContextMenu = ['Search ...']
        if node is None:
            node = self
        else:
            if not hasattr(node,'ContextMenu'):
                node.ContextMenu=[]
            if not 'Search ...' in [k for k,a in node.ContextMenu]: ##Creating default menu
              
                if not hasattr(node,'ExpertMenu'): 
                  setattr(node,'ExpertMenu',self.ExpertMenu)
                  
                def addOption(menu,name,action):
                  if name not in [t[0] for t in menu]:
                    menu.append((name,action))
              
                # DEVICE NODE CONTEXT MENU
                if obj.count('/')==2:
                    
                    addOption(node.ContextMenu,"Open Panel", self.showPanel)
                    addOption(node.ContextMenu,"Show Attributes",self.addAttrToNode)
                    
                    if self.getNodeAdmin(node):
                        addOption(node.ContextMenu,"Go to %s"%self.getNodeAdmin(node),
                            (lambda p=self.getNodeAdmin(node): p and self.findInTree(p)))
                    
                    addOption(node.ContextMenu,'', None)

                    addOption(node.ContextMenu,"Show Properties", self.showProperties)
                    addOption(node.ContextMenu,"Test Device", self.test_device)
                    
                    try:
                      self.astor = fandango.Astor()
                      addOption(node.ContextMenu,'Start Server', self.start_server)
                      addOption(node.ContextMenu,'Stop Server', self.stop_server)
                      addOption(node.ContextMenu,'Device Info', self.device_info)
                    except:
                      self.warning('fandango.Astor() not available to start/stop devices')
                        
                    node.ContextMenu.append(('',None))
                    addOption(node.ExpertMenu,"Show ALL Attributes", lambda s=self:s.addAttrToNode(full=True))
                    
                # ATTRIBUTE NODE CONTEXT MENU
                elif obj.count('/')==3:
                    for k,v in self.AttributeMenu:
                        self.debug('Adding action %s'%k)
                        if type(v) is str and hasattr(self,v):
                            node.ContextMenu.append((k, getattr(self,v)))
                        else:
                            node.ContextMenu.append((k, lambda s=self.getNodeAlias(node): v(s)))
                    #node.ContextMenu.append(("add to Trends", self.addToPlot))
                    #node.ContextMenu.append(("remove from Trends", self.removeFromPlot))
                    node.ContextMenu.append(('',None))
                    
                #node.ContextMenu.append(("Expand Node", self.expandNode))
                #node.ContextMenu.append(("Collapse Node", self.collapseNode))
                
                if node.isExpanded() and node.childCount()<10 and all(self.getNodeText(node.child(j)).count('/')==2 for j in range(node.childCount())):
                    node.ContextMenu.append(("Show Attributes", lambda n=node,s=self: [s.addAttrToNode(n.child(j)) for j in range(n.childCount())]))
                node.ContextMenu.append(("Search ...",\
                    lambda: self.findInTree(str(Qt.QInputDialog.getText(self,'Search ...','Write a part of the name',Qt.QLineEdit.Normal)[0]))
                    ))
        #configDialogAction = menu.addAction("Refresh Tree")
        #self.connect(configDialogAction, Qt.SIGNAL("triggered()"), self.refreshTree)
        menu = Qt.QMenu(self)
        
        if hasattr(node,'ContextMenu'):
            last_was_separator = True
            for t in (type(node.ContextMenu) is dict and node.ContextMenu.items() or node.ContextMenu):
                try:
                    k,action = t
                    if k:
                        configDialogAction = menu.addAction(k)
                        if action: self.connect(configDialogAction, Qt.SIGNAL("triggered()"), action)
                        else: configDialogAction.setEnabled(False)
                        last_was_separator = False
                    elif not last_was_separator: 
                        menu.addSeparator()
                        last_was_separator = True
                except Exception,e: 
                    self.warning('Unable to add Menu Action: %s:%s'%(t,e))
        
        if hasattr(node,'ExpertMenu'):
            menu.addSeparator()
            expert = menu.addMenu('Expert')
            #expert.addSeparator()
            last_was_separator = True
            for t in (type(node.ContextMenu) is dict and node.ExpertMenu.items() or node.ExpertMenu):
                try:
                    k,action = t
                    if k:
                        configDialogAction = expert.addAction(k)
                        if action: self.connect(configDialogAction, Qt.SIGNAL("triggered()"), action)
                        else: configDialogAction.setEnabled(False)
                        last_was_separator = False
                    elif not last_was_separator: 
                        expert.addSeparator()
                        last_was_separator = True
                except Exception,e: 
                    self.warning('Unable to add Expert Action: %s:%s'%(t,e))            
        #menu.addSeparator()
        menu.exec_(event.globalPos())
        del menu
        
    def start_server(self, device=None):
        """
        Allow start Servers.
        :param device: DeviceName
        :return:
        """
        device = device or self.getNodeDeviceName()
        self.astor.load_by_name(device)
        ss = self.astor.get_device_server(device)
        text, ok = Qt.QInputDialog.getText(self, 'Start Server', 'Start %s at '
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
        device = device or self.getNodeDeviceName()
        self.astor.load_by_name(device)
        ss = self.astor.get_device_server(device)
        v = Qt.QMessageBox.warning(self, 'Stop Server', 
            '%s will be killed!, Are you sure?'%ss,
            Qt.QMessageBox.Yes | Qt.QMessageBox.No)
        if v == Qt.QMessageBox.Yes:
            return self.astor.stop_servers(ss)
        else:
            return False

    def device_info(self, device=None):
        """
        Show a the Device Info
        :param device: DeviceName
        :return:
        """
        device = device or self.getNodeDeviceName()
        di = fandango.tango.get_device_info(device)
        txt = '\n'.join('%s : %s' % (k, getattr(di, k)) for k in
                        'name dev_class server host level exported started stopped PID'.split())
        v = Qt.QMessageBox.information(self, device, txt, Qt.QMessageBox.Ok)
        
    def test_device(self):
        import os
        device = str(self.getNodeDeviceName())
        if not device: return
        comm = 'tg_devtest %s &'%device
        os.system(comm)        

class VaccaTree(TaurusSearchTree):
    """
    It is a class that inherits from TaurusSearchTree.
    Allow show the devices and start/stop it with the right button (
    expandable menu)

    """

    # This slots are overloaded here because they are not yet in the last taurus package. Once it will be included in TaurusSearchTree than it can be removed.
    # The slots are needed because the method_forwarder method is not seen from the SharedDataManager side.

    # def __getattr__(self,attr):
    # if attr!='tree':
    # return getattr(self.tree,attr)

    ## DO  NOT REMOVE YET!!
    def setTangoHost(self, *a, **k):
        self.tree.setTangoHost(*a, **k)

    def addModels(self, *a, **k):
        self.tree.addModels(*a, **k)

    def setModel(self, *a, **k):
        self.tree.setModel(*a, **k)

    def setModelCheck(self, *a, **k):
        self.tree.setModelCheck(*a, **k)

    def setTree(self, *a, **k):
        self.tree.setTree(*a, **k)

    def expandAll(self, *a, **k):
        self.tree.expandAll(*a, **k)

    def loadTree(self, *a, **k):
        print('VaccaTree.loadTree(...)')
        self.tree.loadTree(*a, **k)

    @staticmethod
    def setDefaultPanelClass(*a, **k):
        TaurusDevTree.setDefaultPanelClass(*a, **k)

    @staticmethod
    def setDefaultAttrFilter(*a, **k):
        TaurusDevTree.setDefaultAttrFilter(*a, **k)

    @classmethod
    def setIconMap(klass, iconMap):
        TaurusDevTree.setIconMap(iconMap)

    def defineStyle(self):
        # print('In TaurusSearchTree.defineStyle()')
        self.setWindowTitle('VaccaTree')
        self.setLayout(Qt.QVBoxLayout())
        self.edit = TaurusDevTreeOptions(self)
        self.tree = VaccaDevTree(self)
        self.setLogLevel(self.Warning)
        self.tree.setLogLevel(self.Warning)

        self.layout().addWidget(self.edit)
        self.layout().addWidget(self.tree)
        self.registerConfigDelegate(self.tree)
        # Event forwarding ...
        for signal in TaurusDevTree.__pyqtSignals__:
            Qt.QObject.connect(self.tree,
                               Qt.SIGNAL(signal),
                               lambda args,
                                      f=self,
                                      s=signal: f.emit(Qt.SIGNAL(s), args))
            
        self.edit.connectWithTree(self.tree)
        self.statetimer = Qt.QTimer(self)
        self.connect(self.statetimer, Qt.SIGNAL('timeout()'), self.updateStates)
        self.statetimer.start(333)
        return

    def updateStates(self):
        try:
            self.debug('On VaccaTree.updateStates()')
            if not hasattr(self,'_statecount'): self._statecount = 0
            if not self._statecount: 
                self._nodes2update = self.tree.getAllNodes().keys()
                self._allexported = fandango.get_all_devices(exported=True)

            if len(self._nodes2update)>32:
              if getattr(self,'_coloured',True):
                self._coloured = False
                whites = dict((k,'CLOSE') for k in self._nodes2update)
                self.tree.setIcons(whites,regexps=False)
                self.warning('too many tree nodes (%s) to update!'%(len(self._nodes2update)))
              else: pass #Not trivial
            else:
              t0,dct = time.time(),{}
              while time.time() < t0+2e-3:
                  if self._statecount>=len(self._nodes2update):
                      self._statecount = 0
                  k = self._nodes2update[self._statecount]
                  self._statecount+=1 #< must be here
                  try:
                      if k.count('/') == k.count(':')+2:
                          x = k in self._allexported
                          self.debug('On VaccaTree.updateStates(%s,%s,%s)'%(self._statecount,k,x))
                          if not x:
                            self.debug('\t%s not exported!'%k)
                            dct[k] = 'UNKNOWN'
                          else:
                            dct[k] = str(taurus.Attribute(k+'/State').read().value)
                  except:
                      self.info('updateStates(%s) failed!: %s'%(k,traceback.format_exc()))
              if dct:
                  self.tree.setIcons(dct,regexps=False)

        except:
            self.warning('On VaccaTree.updateStates(): %s' % traceback.format_exc())
            
    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        path = 'image/widgets/Tree.png'
        return path


from .doc import get_autodoc

__doc__ = get_autodoc(__name__, vars())

###############################################################################
