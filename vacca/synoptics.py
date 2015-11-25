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

import sys,re,traceback
import fandango,fandango.qt,taurus
from PyQt4 import Qt,Qwt5
from taurus.qt.qtgui.taurusgui.utils import PanelDescription
from taurus.core.taurusvalidator import DeviceNameValidator, AttributeNameValidator
from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, \
    TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE, TAURUS_MODEL_LIST_MIME_TYPE
from taurus import Manager

from taurus.qt import Qt
from fandango import partial,FakeLogger as FL

from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView,TaurusGraphicsScene,TaurusJDrawGraphicsFactory,TYPE_TO_GRAPHICS
from taurus.qt.qtgui.graphic.taurusgraphic import TaurusGroupItem

import traceback
def catched(f):
  def new_f(*args,**kwargs):
    try:
      return f(*args,**kwargs)
    except:
      traceback.print_exc()
  return new_f

class VaccaSynoptic(TaurusJDrawSynopticsView):
    """

    Overrides TaurusJDrawSynopticsView methods to highlight multiple items in multiple colors.
    
    It allows to setup a delayed setModel call to reduce "hungs" on heavy synoptics.
    But!: This delayed call may cause problems in some versions of taurusGUI. (due to scene not-set yet)
    """

    JDRAW_FILE = None
    JDRAW_HOOK = None
    JDRAW_TREE = None

    
    def __init__(self, parent = None, delay=0, designMode = False, updateMode=None, alias = None, resizable = True, panelClass = None):
        self.delay = delay
        TaurusJDrawSynopticsView.__init__(self, parent,designMode,updateMode,alias,resizable,panelClass)
        self.setModelInConfig(False)

    
    def setModel(self, model):
        if self.delay:
            self.warning('VaccaSynoptic.setModel() delayed %d ms'%self.delay)
            self._setter = Qt.QTimer.singleShot(
                self.delay, 
                partial(self._setJDrawModel, model))
            self.JDRAW_FILE = model
        else:
            TaurusJDrawSynopticsView.setModel(self, model)

    
    def _setJDrawModel(self, model):
        print '>'*80
        print 'setJDrawModel(%s)' % model
        TaurusJDrawSynopticsView.setModel(self, model)

    
    def getModelMimeData(self):
        """ Used for drag events """

        model,mimeData = '',None
        try:
            #model = getattr(self.scene().itemAt(*self.mousePos),'_name','')
            selected = self.scene()._selectedItems
            if not selected:
                self.debug('jdrawView.getModelMimeData(%s): nothing to drag'%model)
                return
            model = getattr(([s for s in selected if getattr(s,'_name','')] or [selected])[0],'_name','')
            self.debug('getModelMimeData(%s)'%model)
            mimeData = Qt.QMimeData()
            if model:
                # self.debug('getMimeData(): DeviceModel at %s: %s',self.mousePos,model)
                mimeData.setText(model)
                mimeData.setData(TAURUS_MODEL_MIME_TYPE, model)
                if DeviceNameValidator().getParams(model):
                    self.debug('getMimeData(): DeviceModel at %s: %s',self.mousePos,model)
                    mimeData.setData(TAURUS_DEV_MIME_TYPE,model)
                elif AttributeNameValidator().getParams(model):
                    self.debug('getMimeData(): AttributeModel at %s: %s',self.mousePos,model)
                    mimeData.setData(TAURUS_ATTR_MIME_TYPE,model)
                    mimeData.setData(TAURUS_DEV_MIME_TYPE,model.rsplit('/',1)[0])
                else:
                    self.debug('getMimeData(): UnknownModel at %s: %s',self.mousePos,model)
        except:
            self.debug('jdrawView.getModelMimeData(%s): unable to get MimeData'%model)
            self.debug(traceback.format_exc())
        return mimeData
        
    @staticmethod
    def getPanelDescription(NAME='Synoptic',JDRAW_FILE='',JDRAW_HOOK=None,JDRAW_TREE=[]):
        """

        :param NAME: Name for the Panel
        :param JDRAW_FILE: synoptic configuration file
        :param JDRAW_HOOK: ''
        :param JDRAW_TREE: None
        :return: PanelDescription Object
        """

        # CONNECTING FAKELOGGER FOR DEBUGGING
        try:
            import vacca
            sdm = vacca.utils.get_shared_data_manager()
            if sdm:
                v = sdm._SharedDataManager__models.get('SelectedInstrument')
                # An inline instantiated FakeLogger will print selected instrument on each click
                sdm.connectReader('SelectedInstrument', 
                    FL('SDM.SelectedInstrument [%s,%s]' % 
                       (v.readerCount(),v.writerCount()), True).info,
                    readOnConnect=False)
        except:
            print '#'*80
            print('Shared Data Manager is not available! (no TaurusGUI instance?)')
            traceback.print_exc()
            sdm = None
            print '#'*80


        print '>'*20+'Loading Synoptic panel new ... %s, %s, %s'%\
            (JDRAW_FILE,JDRAW_HOOK,JDRAW_TREE)

        class_name,rsignal,wsignal = '',{},{}            
        if not JDRAW_FILE.endswith('.svg'): #Assuming a JDraw file
            print '>'*20+'Creating JDW VaccaSynoptic'

            if JDRAW_HOOK is not None:
                print 'Enabling JDRAW_HOOK = %s'%JDRAW_HOOK
                from fandango.qt import QSignalHook
                in_hook = QSignalHook(JDRAW_HOOK)
                out_hook = QSignalHook(JDRAW_HOOK)

                #Synoptic will write this signal
                wsignal = {'JDrawOut': 'graphicItemSelected(QString)', }

                if sdm:
                    sdm.connectReader('JDrawOut', FL('SDM.JDrawOut',
                                                     True).info,
                                      readOnConnect=False)
                    sdm.connectReader('JDrawOut', out_hook.setModel,
                                      readOnConnect=False)
                    sdm.connectWriter('SelectedInstrument', out_hook,
                                      'modelChanged')

                    v = sdm._SharedDataManager__models.get('JDrawOut')
                    sdm.connectReader('JDrawOut', FL('SDM.JDrawOut DONE [%s,'
                                                     '%s]'%(v.readerCount(),
                                                            v.writerCount()),
                                                     True).info,
                                      readOnConnect=False)

                    sdm.connectWriter('JDrawIn', in_hook,'modelChanged')
                    sdm.connectReader('JDrawIn', FL('SDM.JDrawIn', True).info,
                                      readOnConnect=False)
                    rsignal = {'JDrawIn': 'selectGraphicItem', }
                    sdm.connectReader('SelectedInstrument', in_hook.setModel,
                                      readOnConnect=False)

                    v = sdm._SharedDataManager__models.get('JDrawIn')
                    sdm.connectReader('JDrawIn', FL('SDM.JDrawIn DONE [%s,'
                                                    '%s]' % (v.readerCount(),
                                                           v.writerCount()),
                                                    True).info,
                                      readOnConnect=False)
            else:
                rsignal = {'SelectedInstrument': 'selectGraphicItem'}
                rsignal['HighlightInstruments'] = 'setHighlightedItems'
                wsignal = {'SelectedInstrument': 'graphicItemSelected(QString)'}

            if JDRAW_TREE:
                wsignal['LoadItems'] = 'modelsChanged'


            class_name='vacca.synoptics.VaccaSynoptic'

        elif JDRAW_FILE.endswith('.svg'):
            try:
                from svgsynoptic import SynopticWidget, Registry
                rsignal = {'SelectedInstrument': 'select_devices'}
                #@TODO: rsignal['HighlightInstruments'] = 'setHighlightedItems'
                wsignal = {'SelectedInstrument': 'graphicItemSelected(QString)'}
                class_name='synoptic.SynopticWidget'
            except:
                print('Horreur!: svgsynoptic MODULE NOT AVAILABLE!')
                return None

        print 'Out of VaccaSynoptic.getPanelDescription(%s,%s)'%(class_name,JDRAW_FILE)
        return PanelDescription(NAME,
                                #classname = 'vacca.VacuumSynoptic',
                                classname=class_name,
                                model=JDRAW_FILE, #Model loading is delayed by
                                # VacuumSynoptic method
                                sharedDataRead=rsignal,
                                sharedDataWrite=wsignal,
                                )        

    ###########################################################################
    # OVERLOADED METHODS FOR CUSTOM HIGHLITHING
    # It should be included in Taurus as patches
    
    
    def setHighlightedItems(self, models = [], color=Qt.Qt.red):
        """

        :param models: List of model to be Highlighted
        :param color: Color, by default Qt.Qt.red
        """
        if fandango.isSequence(models):
            models = '(%s)'%')|('.join(models)
        self.info('setHighLightedItems(%s)' % models)
        try:
            default = self.scene().selectionColor()
            self.scene().setSelectionColor(color)
            self.scene().selectGraphicItem(models)
            self.scene().setSelectionColor(default)
        except:
            err = traceback.format_exc()
            self.error(err)
        finally:
            self.scene().setSelectionColor(default)
    
    
    def getGraphicsFactory(self,delayed=False):
        return VaccaSynopticGraphicsFactory(self,alias=(self.alias or None),delayed=delayed)
    
    @staticmethod
    def getDefaultIcon():
        """
        :return: The Default Icon Path.
        """
        path = 'image/icons/Synoptic.png'
        return path

#A decorator for QGraphics Objects
def GetClassWithExtensions(klass):
    class ClassWithExtensions(klass):
        
        
        def setName(self,name):
            name = str(name or self.__class__.__name__)
            self._name = name#srubio@cells.es: modified to store ._name since initialization (even if a model is not set)
        
        
        def getExtensions(self):
            """
            Any in
            ExtensionsList,noPrompt,standAlone,noTooltip,noSelect,ignoreRepaint,shellCommand,className,classParams
            """
            self._extensions = getattr(self,'_extensions',{})
            if 'ExtensionsList' in self._extensions:
                self._extensions.update((k.strip(),True) for k in self._extensions['ExtensionsList'].split(','))
                self._extensions.pop('ExtensionsList')
            for k in ('noPrompt','standAlone','noTooltip','ignoreRepaint','noSelect'):
                if self._extensions.get(k,None)=='': self._extensions[k] = True
            self.noPrompt = self._extensions.get('noPrompt',False)
            self.standAlone = self._extensions.get('standAlone',False)
            self.noTooltip = self._extensions.get('noTooltip',False)
            self.ignoreRepaint = self._extensions.get('ignoreRepaint', getattr(self,'ignoreRepaint',False))
            self.setName(self._extensions.get('name',self._name))
            tooltip = '' if (self.noTooltip or self._name==self.__class__.__name__ or self._name is None) else str(self._name)
            #self.debug('setting %s.tooltip = %s'%(self._name,tooltip))
            self.setToolTip(tooltip)
            #self.debug('%s.getExtensions(): %s'%(self._name,self._extensions))
            return self._extensions
    return ClassWithExtensions

class VaccaSynopticGraphicsFactory(TaurusJDrawGraphicsFactory):

    
    def getSceneObj(self,items):
        scene = VaccaGraphicsScene(self.myparent)
        for item in items:
            try:
                if isinstance(item, Qt.QWidget):
                    scene.addWidget(item)
                elif isinstance(item, Qt.QGraphicsItem):
                    scene.addItem(item)
            except:
                self.warning("Unable to add item %s to scene" % str(item))
                self.debug("Details:", exc_info=1)
        return scene
    
    
    def getGraphicsItem(self,type_,params):
        name = params.get(self.getNameParam())
        #applying alias
        for k,v in getattr(self,'alias',{}).items():
            if k in name:
                name = str(name).replace(k,v)
                params[self.getNameParam()] = name
        cls = None
        if '/' in name:
            #replacing Taco identifiers in %s'%name
            if name.lower().startswith('tango:') and (name.count('/')==2 or not 'tango:/' in name.lower()): 
                nname = name.split(':',1)[-1]
                params[self.getNameParam()] = name = nname
            if name.lower().endswith('/state'): name = name.rsplit('/',1)[0]
            cls = Manager().findObjectClass(name)
        else: 
            if name: self.debug('%s does not match a tango name'%name)
        klass = self.getGraphicsClassItem(cls, type_)
        self.debug(str((cls,type_,klass,klass.__name__)))
        if not hasattr(klass,'getExtensions'):
            klass = GetClassWithExtensions(klass)
        item = klass()
        ## It's here were Attributes are subscribed
        self.set_common_params(item,params)
        if hasattr(item,'getExtensions'):
            item.getExtensions() #<= must be called here to take extensions from params
        return item    
    
class VaccaGraphicsScene(TaurusGraphicsScene):
        
    
    def setSelectionColor(self,color):
        self._selectioncolor = color
        
    
    def selectionColor(self):
        try:
            assert self._selectioncolor
        except:
            self._selectioncolor = Qt.Qt.blue
        return self._selectioncolor
        
    
    def _displaySelectionAsOutline(self, items):
        def _outline(shapes):
            """"Compute the boolean union from a list of QGraphicsItem. """
            shape = None
            # TODO we can use a stack instead of recursivity
            for s in shapes:
                # TODO we should skip text and things like that
                if isinstance(s, TaurusGroupItem):
                    s = _outline(s.childItems())
                    if s == None:
                        continue

                s = s.shape()
                if shape != None:
                    shape = shape.united(s)
                else:
                    shape = s

            if shape == None:
                return None

            return Qt.QGraphicsPathItem(shape)

        # TODO we can cache the outline instead of computing it again and again
        selectionShape = _outline(items)
        if selectionShape:
            # copy-paste from getSelectionMark
            color = Qt.QColor(self.selectionColor())
            color.setAlphaF(.10)
            pen = Qt.QPen(Qt.Qt.SolidLine)
            pen.setWidth(4)
            pen.setColor(Qt.QColor(self.selectionColor()))
            selectionShape.setBrush(color)
            selectionShape.setPen(pen)

            for item in items:
                if item not in self._selectedItems: self._selectedItems.append(item)

            # TODO i dont think this function work... or i dont know how...
            #self.setSelectionMark(picture=selectionShape)
            # ... Then do it it with hands...
            # copy-paste from drawSelectionMark
            self._selection.append(selectionShape)
            # It's better to add it hidden to avoid resizings
            selectionShape.hide()
            self.addItem(selectionShape)
            # Put on Top
            selectionShape.setZValue(9999)
            selectionShape.show()
            self.updateSceneViews()

            return True

        return False
    
    
    def getSelectionMark(self,picture=None,w=10,h=10):
        if picture is None:
            if self.SelectionMark:
                SelectionMark = self.SelectionMark()
            else:
                SelectionMark = Qt.QGraphicsEllipseItem()
                color = Qt.QColor(self.selectionColor())
                color.setAlphaF(.10)
                SelectionMark.setBrush(color)
                pen = Qt.QPen(Qt.Qt.CustomDashLine)
                pen.setWidth(4)
                pen.setColor(Qt.QColor(self.selectionColor()))
                SelectionMark.setPen(pen)
                SelectionMark.hide() #It's better to add it hidden to avoid resizings                
        else:
            try:
                if isinstance(picture,Qt.QGraphicsItem):
                    SelectionMark = picture
                    SelectionMark.setRect(0,0,w,h)
                    SelectionMark.hide()
                elif operator.isCallable(picture):
                    SelectionMark = picture()
                else:
                    if isinstance(picture,Qt.QPixmap):
                        pixmap = picture
                    elif isinstance(picture,basestring) or isinstance(picture,Qt.QString):
                        picture = str(picture)
                        pixmap = Qt.QPixmap(os.path.realpath(picture))
                    SelectionMark = Qt.QGraphicsPixmapItem()
                    SelectionMark.setPixmap(pixmap.scaled(w,h))
                    SelectionMark.hide()
            except:
                self.debug('In setSelectionMark(%s): %s'%(picture,traceback.format_exc()))
                picture = None
        return SelectionMark
    
    ##################################################################
    
    
    def getItemByPosition(self,x,y):
        """ This method will try first with named objects; if failed then with itemAt """
        pos = Qt.QPointF(x,y)
        itemsAtPos = []
        for z,o in sorted((i.zValue(),i) for v in self._itemnames.values() for i in v if i.contains(pos) or i.isUnderMouse()):
            if not hasattr(o,'getExtensions'):
                self.warning('getItemByPosition(%d,%d): adding Qt primitive %s'%(x,y,o))
                itemsAtPos.append(o)
            elif not o.getExtensions().get('noSelect'):
                self.warning('getItemByPosition(%d,%d): adding GraphicsItem %s'%(x,y,o))
                itemsAtPos.append(o)
            else: self.warning('getItemByPosition(%d,%d): object ignored, %s'%(x,y,o))
        if itemsAtPos:
            obj = itemsAtPos[-1]
            return self.getTaurusParentItem(obj) or obj
        else: 
            #return self.itemAt(x,y)
            self.debug('getItemByPosition(%d,%d): no items found!'%(x,y))
            return None    
        
    #def getItemClicked(self,mouseEvent):
        #pos = mouseEvent.scenePos()
        #x,y = pos.x(),pos.y()
        #self.emit(Qt.SIGNAL("graphicSceneClicked(QPoint)"),Qt.QPoint(x,y))
        #obj = self.getItemByPosition(x,y)
        ##self.debug('mouse clicked on %s(%s) at (%s,%s)'%(type(obj).__name__,getattr(obj,'_name',''),x,y))
        #return obj        

    #def mousePressEvent(self,mouseEvent):
        ##self.debug('In TaurusGraphicsScene.mousePressEvent(%s,%s))'%(str(type(mouseEvent)),str(mouseEvent.button())))
        #try: 
            #obj = self.getItemClicked(mouseEvent)
            #obj_name = getattr(obj,'_name', '')
            #if not obj_name and isinstance(obj,QGraphicsTextBoxing): obj_name = obj.toPlainText()
            #if (mouseEvent.button() == Qt.Qt.LeftButton):
                ### A null obj_name should deselect all, we don't send obj because we want all similar to be matched                
                #if self.selectGraphicItem(obj_name):
                    #self.debug(' => graphicItemSelected(QString)(%s)'%obj_name)
                    #self.emit(Qt.SIGNAL("graphicItemSelected(QString)"),obj_name)
                #else:
                    ## It should send None but the signature do not allow it
                    #self.emit(Qt.SIGNAL("graphicItemSelected(QString)"), "")
            #def addMenuAction(menu,k,action,last_was_separator=False):
                #try:
                    #if k:
                        #configDialogAction = menu.addAction(k)
                        #if action: 
                            #self.connect(configDialogAction, Qt.SIGNAL("triggered()"), lambda dev=obj_name,act=action: act(dev))
                        #else: configDialogAction.setEnabled(False)
                        #last_was_separator = False
                    #elif not last_was_separator: 
                        #menu.addSeparator()
                        #last_was_separator = True
                #except Exception,e: 
                    #self.warning('Unable to add Menu Action: %s:%s'%(k,e))                    
                #return last_was_separator
            #if (mouseEvent.button() == Qt.Qt.RightButton):
                #''' This function is called when right clicking on TaurusDevTree area. A pop up menu will be shown with the available options. '''
                #self.debug('RightButton Mouse Event on %s'%(obj_name))
                #if isinstance(obj,TaurusGraphicsItem) and (obj_name or obj.contextMenu() or obj.getExtensions()):
                    #menu = Qt.QMenu(None)#self.parent)    
                    #last_was_separator = False
                    #extensions = obj.getExtensions()
                    #if obj_name and (not extensions or not extensions.get('className')): 
                        ##menu.addAction(obj_name)
                        #addMenuAction(menu,'Show %s panel'%obj_name,lambda x=obj_name: self.showNewPanel(x))
                    #if obj.contextMenu():
                        #if obj_name: 
                            #menu.addSeparator()
                            #last_was_separator = True
                        #for t in obj.contextMenu(): #It must be a list of tuples (ActionName,ActionMethod)
                            #last_was_separator = addMenuAction(menu,t[0],t[1],last_was_separator)
                    #if extensions:
                        #if not menu.isEmpty(): menu.addSeparator()
                        #className = extensions.get('className')
                        #if className and className!='noPanel':
                            #self.debug('launching className extension object')
                            #addMenuAction(menu,'Show %s'%className,lambda d,x=obj: self.showNewPanel(x))
                        #if extensions.get('shellCommand'):
                            #addMenuAction(menu,'Execute',lambda d,x=obj: self.getShellCommand(x))
                    #if not menu.isEmpty():
                        #menu.exec_(Qt.QPoint(mouseEvent.screenPos().x(),mouseEvent.screenPos().y()))
                    #del menu
        #except Exception:
            #self.warning( traceback.format_exc())

###############################################################################

import doc
__doc__ = doc.get_autodoc(__name__,vars())

def test(model,filters='',debug=False):
    
    if debug: 
        taurus.setLogLevel(taurus.core.util.Logger.Debug)

    print 'loading synoptic: %s'%model
    form = VaccaSynoptic(delay=1000,designMode=False)
    #form = taurus.qt.qtgui.graphic.TaurusJDrawSynopticsView(designMode=False)
    #designMode=False,updateMode=VaccaSynoptic.NoViewportUpdate)
    form.show()
    form.setModel(model)
    form.setWindowTitle(model)
    print 'showing ...'
    return form

if __name__ == '__main__':
    #!/usr/bin/python
    assert len(sys.argv)>1, '\n\nUsage:\n\t> python synoptic [jdw file]'
    
    app = Qt.QApplication([]) #sys.argv)

    model = sys.argv[1]
    filters = fandango.first(sys.argv[2:],'')
    form = test(model,filters)

    sys.exit(app.exec_())
