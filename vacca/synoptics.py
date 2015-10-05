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

from taurus.qt import Qt
from fandango import partial,FakeLogger as FL

from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView,TaurusGraphicsScene,TaurusJDrawGraphicsFactory
from taurus.qt.qtgui.graphic.taurusgraphic import TaurusGroupItem


class VaccaSynoptic(TaurusJDrawSynopticsView):

    JDRAW_FILE = None
    JDRAW_HOOK = None
    JDRAW_TREE = None

    def __init__(self, *args, **kwargs):
        TaurusJDrawSynopticsView.__init__(self, *args, **kwargs)
        self.setModelInConfig(False)

    def setModel(self, model):
        from fandango import partial
        self._setter = Qt.QTimer.singleShot(3000, partial(
            self._setJDrawModel, model))
        self.JDRAW_FILE = model



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
            
        if JDRAW_FILE.endswith('.jdw'):
            print '>'*20+'Creating VaccaSynoptic'

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
            from svgsynoptic import SynopticWidget, Registry
            rsignal = {'SelectedInstrument': 'select_devices'}
            #@TODO: rsignal['HighlightInstruments'] = 'setHighlightedItems'
            wsignal = {'SelectedInstrument': 'graphicItemSelected(QString)'}

            class_name='synoptic.SynopticWidget'
            # synoptic = PanelDescription('Synoptic',
            #                     #classname = 'vacca.VacuumSynoptic',
            #                     classname='svgsynoptic.SynopticWidget',
            #                     model=jdraw_file, #Model loading is delayed by
            #                     # VacuumSynoptic method
            #                     sharedDataRead=rsignal,
            #                     sharedDataWrite=wsignal,
            #                     )
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
        if fandango.isSequence(models):
            models = '(%s)'%')|('.join(models)
        self.warning('setHighLightedItems(%s)' % models)
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

###############################################################################

def test(model):
    taurus.setLogLevel(taurus.core.util.Logger.Debug)
    assert len(sys.argv)>1, '\n\nUsage:\n\t> python synoptic [jdw file]'
    try: 
        app = Qt.QApplication([]) #sys.argv)
    except:
        pass
    
    filters = fandango.first(sys.argv[2:],'')
    form = None
    if model.lower().endswith('.jdw'):
        print 'loading a synoptic'
        form = VaccaSynoptic()
        #designMode=False,updateMode=VaccaSynoptic.NoViewportUpdate)
        form.setModel(model)

    print 'showing ...'
    form.show()
    return form

if __name__ == '__main__':
    #!/usr/bin/python
    assert len(sys.argv)>1, '\n\nUsage:\n\t> python synoptic [jdw file]'
    model = sys.argv[1]
    form = test(model = sys.argv[1])
    sys.exit(fandango.qt.getApplication().exec_())
