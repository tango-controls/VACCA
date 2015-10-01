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


import fandango
import fandango.qt
import fandango.functional as fun
from PyQt4 import Qt,Qwt5
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

from taurus.qt import Qt
from fandango import partial,FakeLogger as FL

from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView


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


    #def selectGraphicItem(self,item_name):
        #item = self.scene().selectGraphicItem(item_name)
        #MimeData = self.getModelMimeData()
        #print repr(MimeData)
        #print "SelectedGraphicItem in VaccaSynoptic: %s, %s"%(item_name, MimeData)
        #return False

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
                wsignal = {'SelectedInstrument': 'graphicItemSelected(QString)'}

            if JDRAW_TREE:
                wsignal['LoadItems'] = 'modelsChanged'


            class_name='vacca.synoptics.VaccaSynoptic'

        elif JDRAW_FILE.endswith('.svg'):
            from svgsynoptic import SynopticWidget, Registry
            rsignal = {'SelectedInstrument': 'select_devices'}
            wsignal = {'SelectedInstrument': 'graphicItemSelected(QString)'}

            class_name='svgsynoptic.SynopticWidget'
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



if __name__ == '__main__':
    #!/usr/bin/python
    import sys,re,traceback,taurus
    taurus.setLogLevel(taurus.core.util.Logger.Debug)
    app = Qt.QApplication(sys.argv)
    assert len(sys.argv)>1, '\n\nUsage:\n\t> python synoptic [jdw file]'
    model = sys.argv[1]
    filters = fun.first(sys.argv[2:],'')
    form = None
    if model.lower().endswith('.jdw'):
        print 'loading a synoptic'
        #form = taurus.qt.qtgui.graphic.TaurusJDrawSynopticsView(
        #    designMode=False,
        #  updateMode=taurus.qt.qtgui.graphic.TaurusJDrawSynopticsView
        #      .NoViewportUpdate
        #  )
        form = VaccaSynoptic(
            designMode=False,
          updateMode=VaccaSynoptic.NoViewportUpdate
          )


        form.setModel(model)
        # models = form.get_item_list()
        # for m in models:
        #     m = str(m)
        #     if m.count('/') == 2:
        #         m += '/state'
        #     period = 120000.
        #     try:
        #         taurus.Attribute(m).changePollingPeriod(period)
        #     except:
        #         print '(%s).changePollingPeriod(%s): Failed: %s' % (m,
        #                                                             period,
        #                                                 traceback.format_exc()
        #                                                             )
    print 'showing ...'
    form.show()
    sys.exit(app.exec_())
