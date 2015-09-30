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
import fandango.functional as fun
from PyQt4 import Qt,Qwt5
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

from taurus.qt import Qt
from fandango import partial,FakeLogger as FL

from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView


class VaccaSynoptic(fandango.qt.Draggable(TaurusJDrawSynopticsView)):

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


    def selectGraphicItem(self,item_name):
        item = self.scene().selectGraphicItem(item_name)
        MimeData = self.getModelMimeData()
        print repr(MimeData)
        print "SelectedGraphicItem in VaccaSynoptic: %s, %s"%(item_name, MimeData)
        return False

    def getPanelDescription(self):

        # TODO: Replace sdm to fandango.utils.getSMD()
        try:
            import vacca
            sdm = vacca.utils.get_shared_data_manager()
            if sdm:

                v = sdm._SharedDataManager__models.get('SelectedInstrument')
                sdm.connectReader('SelectedInstrument', FL('SDM.SelectedInstrument ['
                                                   '%s,%s]' % (v.readerCount(),
                                                             v.writerCount(

                                                             )), True).info,
                          readOnConnect=False)
        except:
            print '#'*80
            print('Shared Data Manager is not available! (no TaurusGUI instance?)')
            traceback.print_exc()
            sdm = None
            print '#'*80



        print '>'*20+'Loading Synoptic panel new ... %s, %s, ' \
                     '%s'%(self.JDRAW_FILE,self.JDRAW_HOOK,
                                                              self.JDRAW_TREE)
        if self.JDRAW_FILE.endswith('.jdw'):
            print '>'*20+'Creating VaccaSynoptic'

            if self.JDRAW_HOOK is not None:
                print 'Enabling JDRAW_HOOK = %s'%self.JDRAW_HOOK
                from fandango.qt import QSignalHook
                in_hook = QSignalHook(self.JDRAW_HOOK)
                out_hook = QSignalHook(self.JDRAW_HOOK)

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

            if self.JDRAW_TREE:
                wsignal['LoadItems'] = 'modelsChanged'


            self.class_name='vacca.synoptics.VaccaSynoptic'

        elif self.JDRAW_FILE.endswith('.svg'):
            from svgsynoptic import SynopticWidget, Registry
            rsignal = {'SelectedInstrument': 'select_devices'}
            wsignal = {'SelectedInstrument': 'graphicItemSelected(QString)'}

            self.class_name='svgsynoptic.SynopticWidget'
            # synoptic = PanelDescription('Synoptic',
            #                     #classname = 'vacca.VacuumSynoptic',
            #                     classname='svgsynoptic.SynopticWidget',
            #                     model=jdraw_file, #Model loading is delayed by
            #                     # VacuumSynoptic method
            #                     sharedDataRead=rsignal,
            #                     sharedDataWrite=wsignal,
            #                     )
        return PanelDescription('Synoptic',
                                #classname = 'vacca.VacuumSynoptic',
                                classname=self.class_name,
                                model=self.JDRAW_FILE, #Model loading is delayed by
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
