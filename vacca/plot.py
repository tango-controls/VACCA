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

import traceback,time
import fandango
import PyTango
import taurus
from taurus.qt import Qt
from taurus.qt.qtgui.plot import TaurusTrend,TaurusPlot
from PyTangoArchiving.widget.trend import ArchivingTrend
from taurus.qt.qtgui.panel import TaurusDevicePanel
from PyQt4 import Qwt5
from fandango.qt import Draggable

__doc__ = """
Plots in VACCA have several setups:

 * ApplyConfig is disabled, to avoid previous configs to override trend behavior
 * Default Trend length has several hours instead of seconds.
 * Archiving is still disabled, but also Scale change warnings when re-enabled.
 
"""

TREND_CLASS = TaurusTrend #TaurusArchivingTrend

class PressureTrend(TREND_CLASS):
        
    def showEvent(self, event):
        if not getattr(self, '_tuned', False):
            setup_pressure_trend(self)
            setattr(self, '_tuned', True)
        TREND_CLASS.showEvent(self, event)
        
class VaccaTrend(TREND_CLASS):
    
    def showEvent(self, event):
        if not getattr(self, '_tuned', False):
            setup_pressure_trend(self,log=False,length=4*3600)
            setattr(self, '_tuned', True)
        TREND_CLASS.showEvent(self, event)

def setup_pressure_trend(tt,log=True,length=12*3600):
    print '*'*80
    print 'in setup_pressure_trend(%s,length=%s s)' % (tt, length)
    from PyQt4 import Qwt5
    try:
        #n,w = str(qtw.tabText(qtw.count()-1)),qtw.widget(qtw.count()-1)
        #qtw.insertTab(0,w,n)
        tt.setXDynScale(True)
        xMax = time.time() #tt.axisScaleDiv(Qwt5.QwtPlot.xBottom).upperBound()
        #xMin = tt.axisScaleDiv(Qwt5.QwtPlot.xBottom).lowerBound()
        rg = length #abs(self.str2deltatime(str(self.ui.xRangeCB.currentText())))
        xMin = xMax-rg
        tt.setAxisScale(Qwt5.QwtPlot.xBottom, xMin, xMax)
        if log:
            tt.setAxisScaleType(Qwt5.QwtPlot.yLeft,
                Qwt5.QwtScaleTransformation.Log10)
            #tt.setAxisScale(Qwt5.QwtPlot.yLeft,1e-11,1e-2)
        tt.setUseArchiving(False)
        tt.setModelInConfig(False)
        tt.disconnect(tt.axisWidget(tt.xBottom), 
            Qt.SIGNAL("scaleDivChanged ()"),tt._scaleChangeWarning)
        #tt.setCurvesYAxis([tcs],tt.yRight)
        #: Disabling loading of configuration from file; to avoid a faulty setup to continuously crash the application.
        setattr(tt, 'applyConfig', (lambda *k, **kw: None))
    except:
        print 'Exception in set_pressure_trend(%s)' % tt
        print traceback.format_exc()
    print '*'*80

class VaccaProfilePlot(Draggable(TaurusPlot)):
    
    #def getModelClass(self):
        #return taurus.core.TaurusDevice
    def __init__(self, *args, **kwargs):
        TaurusPlot.__init__(self, *args, **kwargs)
        self._profile_loaded = False
        self._positions = []
        self._labels = []
        self.setModelInConfig(False)
        
    def setModel(self, model):
        print '*'*80
        self.info('VaccaProfilePlot.setModel(%s)' % model)
        print '*'*80
        try:
            #if self._profile_loaded: return
            if fandango.isSequence(model) or 'attributename' in fandango.tango.parse_tango_model(model):
                self.info('setting an attribute model')
                TaurusPlot.setModel(self, model)# model = model[0]# str(
                # model).rsplit('/',1)[0]
            else:
                self.info('setting a composer model')
                assert fandango.check_device(model)
                dev = taurus.Device(model)
                if all(a in map(str.lower, dev.get_attribute_list()) for a in
                    ('ccgaxxis', 'ccgpressures', 'ipaxxis', 'ippressures',
                    'thermoaxxis', 'thermocouples', 'axxispositions',
                     'axxislabels')):
                    TaurusPlot.setModel(self, [])
                    setup_profile_plot(self, model)
                else:
                    self.warning('%s has not all required attributes' % model)
            if len(self._positions) and len(self._labels):
                self.info('Setting CustomXLabels ...')
                self.setAxisCustomLabels(Qwt5.QwtPlot.xBottom,
                                         zip(self._positions, self._labels), 60)
        except Exception, e:
            self.warning('VaccaProfilePlot.setModel(%s) failed!: %s' % (model, e))
            
def setup_profile_plot(tp, composer, picker=True):
    #,gauges,pumps,tcs,positions=None,labels=None):
    """ This method configures a tau plot to show pressure/temperature profiles """
    tp.info('setup_profile_plot(%s,%s)' % (composer, picker))
    #tp.setModel('BO/VC/Composer/IPAxxis|BO/VC/Composer/IPPressures')
    #tp.setModel('BO/VC/Composer/CCGAxxis|BO/VC/Composer/CCGPressures,BO/VC/Composer/IPPressures')
    #positions = [0,17,31,33,49,63,80,94,111,114,116,122]
    #labels=['Q1A','Q1B','Q1LTB','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B','Q4BT','Q4C','Q4D+RF']
    gauges = '%s/CCGAxxis|%s/CCGPressures' % (composer, composer)
    pumps = '%s/IPAxxis|%s/IPPressures' % (composer, composer)
    tcs = '%s/ThermoAxxis|%s/Thermocouples' % (composer, composer)
    positions = '%s/AxxisPositions' % composer
    labels = '%s/AxxisLabels' % composer
                
    pumps, gauges, tcs = [str(s).lower() for s in (pumps, gauges, tcs)]
    tp.setModelInConfig(False)
    tp.setModifiableByUser(False)
    tp.setModel(pumps)
    tp.addModels([tcs])
    tcs = tcs.split('|')[-1]
    tp.setCurvesYAxis([tcs], tp.yRight)
    tp.addModels([gauges])
    gauges = gauges.split('|')[-1]
    Curves = {}
    for cname in (pumps, gauges, tcs):
        tp.info('set curve %s' % cname)
        try:
            Curves[cname] = tp.curves[cname]
        except:
            Curves[cname] = tp.curves[cname.split('|')[-1]]
        
    if positions and labels:
        tp.info('Setting CustomXLabels ...')
        try:
            tp._positions = list(int(i) for i in taurus.Attribute(positions).read().value)
            tp._labels = list(str(i) for i in taurus.Attribute(labels).read().value)
            tp.setAxisCustomLabels(Qwt5.QwtPlot.xBottom,zip(tp._positions,
                                                            tp._labels), 60)
        except:
            print 'Unable to read pressure profile labels'
            tp._positions = []
            tp._labels = []
            #print traceback.format_exc()
    
    for cname, color, width in [(gauges, Qt.Qt.blue, 3), (pumps,
                                                          Qt.Qt.magenta, 1),
                                (tcs, Qt.Qt.red, 2)]:
        cap = Curves[cname].getAppearanceProperties()
        cap.lColor = color
        cap.lWidth = width
        tp.setCurveAppearanceProperties({Curves[cname].getCurveName(): cap})
        
    Curves[gauges].setSymbol(Qwt5.QwtSymbol(Qwt5.QwtSymbol.Diamond,
                                            Qt.QBrush(Qt.Qt.yellow),
                                            Qt.QPen(Qt.Qt.green),
                                            Qt.QSize(7, 7)
                                            )
                             )
    #f1 = Qwt5.QwtSplineCurveFitter()
    #f1.setSplineSize(2000)
    #Curves[pumps].setCurveFitter(f1)
    #Curves[pumps].setCurveAttribute(Curves[pumps].Fitted,True)
    tp.enableAxis(tp.yRight)        
    tp.setAxisScaleType(Qwt5.QwtPlot.yLeft, Qwt5.QwtScaleTransformation.Log10)
    #tp.setAxisScale(Qwt5.QwtPlot.yLeft,1e-11,1e-4)
    tp.setCanvasBackground(Qt.Qt.white)
    tp.toggleDataInspectorMode(True)
    tp.showMaxPeaks(True)
    Curves[pumps].showMaxPeak(False)
    tp.setAllowZoomers(False)
    tp.toggleDataInspectorMode(True)
    
    if picker:
        tp.info('setting Picker ...')
        tp.disconnect(tp._pointPicker, Qt.SIGNAL('selected(QwtPolygon)'),
                      tp.pickDataPoint)
        tp.connect(
            tp._pointPicker, 
            Qt.SIGNAL('selected(QwtPolygon)'), 
            lambda pos, s = tp: pickPlotPoint(s, pos, xlabels=(zip(
                tp._positions, tp._labels) if tp._positions and tp._labels
                                                               else None))
            )

    tp._profile_loaded = True
    return tp    
    
def pickPlotPoint(self, pos, scope=20, showMarker=True,
                  targetCurveNames=None, xlabels=None):
    '''Finds the pyxel-wise closest data point to the given position. The
    valid search space is constrained by the scope and targetCurveNames
    parameters.

    :param pos: (Qt.QPoint or Qt.QPolygon) the position around which to look
                for a data point. The position should be passed as a
                Qt.QPoint (if a Qt.QPolygon is given, the first point of the
                polygon is used). The position is expected in pixel units,
                with (0,0) being the top-left corner of the plot
                canvas.

    :param scope: (int) defines the area around the given position to be
                    considered when searching for data points. A data point is
                    considered within scope if its manhattan distance to
                    position (in pixels) is less than the value of the scope
                    parameter. (default=20)

    :param showMarker: (bool) If True, a marker will be put on the picked
                        data point. (default=True)

    :param targetCurveNames: (sequence<str>) the names of the curves to be
                                searched. If None passed, all curves will be
                                searched

    :return: (tuple<Qt.QPointF,str,int> or tuple<None,None,None>) if a point
                was picked within the scope, it returns a tuple containing the
                picked point (as a Qt.QPointF), the curve name and the index of
                the picked point in the curve data. If no point was found
                within the scope, it returns None,None,None
    '''
    print "pickPlotPoint(...)"
    if isinstance(pos, Qt.QPolygon):
        pos = pos.first()
    scopeRect = Qt.QRect(0, 0, scope, scope)
    scopeRect.moveCenter(pos)
    mindist = scope
    picked = None
    pickedCurveName = None
    pickedIndex = None
    self.curves_lock.acquire()
    try:
        if targetCurveNames is None:
            targetCurveNames = self.curves.keys()
        #print '%d targetCurveNames'%len(targetCurveNames)
        for name in targetCurveNames:
            curve = self.curves.get(name, None)
            if curve is None: 
                #print("Curve '%s' not found"%name)
                continue
            if not curve.isVisible(): 
                #print("Curve '%s' not visible"%name)
                continue
            data=curve.data()
            #print("Curve '%s' has %d points"%(name,data.size()))
            for i in xrange(data.size()):
                point = Qt.QPoint(self.transform(curve.xAxis(), data.x(i)),
                                 self.transform(curve.yAxis(), data.y(i))
                                  )
                if scopeRect.contains(point):
                    #print( 'Comparing %s,%s vs %s'%(pos,scopeRect,point))
                    dist = (pos-point).manhattanLength()
                    if dist < mindist:
                        mindist = dist
                        picked = Qt.QPointF(data.x(i), data.y(i))
                        pickedCurveName = name
                        pickedIndex = i
                        pickedAxes = curve.xAxis(), curve.yAxis()
                        found = True
            #if picked: print("Curve '%s' contains %s"%(name,pos))
    finally:
        self.curves_lock.release()
    
    if picked is None:
        print 'pickPlotPoint(%s)> No matching point found for any curve' % pos
        return
    
    xlabels = xlabels or []
    print("pickPlotPoint(x=%s,y=%s,xlabels=[%s])" % (picked.x(), picked.y(),
                                                     len(xlabels)
                                                     ))

    if showMarker and picked is not None:
        print 'showing pickedMarker'
        self._pickedMarker.detach()
        self._pickedMarker.setValue(picked)
        self._pickedMarker.setAxis(*pickedAxes)
        self._pickedMarker.attach(self)
        self._pickedCurveName = pickedCurveName
        self._pickedMarker.pickedIndex = pickedIndex
        self.replot()
        label = self._pickedMarker.label()
        try: 
            xi, xl = ([(x[0], x[1]) for x in (xlabels or []) if x[
                0] <= picked.x()] or [[-1, None]])[-1]
            c = self.curves[pickedCurveName]
            #xc = [self.transform(c.xAxis(),x) for x in c.data().xData()]
            xc = [x for x in c.data().xData()]
            xx = len([x for x in xc if x >= xi and x <= picked.x()])
            #print [x[0] for x in xlabels]
            #print 'picked point: %s'%picked.x()
            #print 'last label %s at %s'%(xl,xi)
            #print 'data point are %s'%(xc)
            #print 'data points between pick and label: %s'%xx
            index = xx
            tag = '%s-%02d' % (xl, index)
            if xl and '/ip' in pickedCurveName.lower():
                try:
                    tag = PyTango.AttributeProxy(tag.replace('-', '/VC/IP-')
                                                 +'/Controller').read().value
                except:
                    import traceback
                    print traceback.format_exc()
        except: 
            import traceback
            print traceback.format_exc()
            index, xl = (-1, None)
            tag = ''
        if xl:
            infotxt = "'%s'[%i]:\n\t (%s,%.2e)" % (pickedCurveName,
                                                  pickedIndex, tag, picked.y())
        elif self.getXIsTime():
            infotxt = "'%s'[%i]:\n\t (x=%s,%.3g)"%(pickedCurveName,
                                                   pickedIndex,
                                                   datetime.fromtimestamp(
                                                       picked.x()).ctime(),
                                                   picked.y()
                                                   )
        else:
            infotxt = "'%s'[%i]:\n\t (x=%.3g, y=%.3g)" % (pickedCurveName,
                                                         pickedIndex,
                                                          picked.x(),
                                                          picked.y())
        label.setText(infotxt)
        print '\t%s' % infotxt
        fits = label.textSize().width() < self.size().width()
        if fits:
            label.setText(infotxt)
            self._pickedMarker.setLabel(Qwt5.QwtText (label))
            self._pickedMarker.alignLabel()
            self.replot()
        else:
            popup = Qt.QWidget(self, Qt.Qt.Popup)
            popup.setLayout(Qt.QVBoxLayout())
            popup.layout().addWidget(Qt.QLabel(infotxt))  #@todo: make the widget background semitransparent green!
            popup.setWindowOpacity(self._pickedMarker.labelOpacity)
            popup.show()
            popup.move(self.pos().x()-popup.size().width(), self.pos().y())
            popup.move(self.pos())
            Qt.QTimer.singleShot(5000, popup.hide)
        
    return picked,pickedCurveName,pickedIndex

import doc
__doc__ = doc.get_autodoc(__name__,vars())

if __name__ == '__main__':
    import taurus.qt.qtgui.application
    app = taurus.qt.qtgui.application.TaurusApplication()
    cmps = fandango.get_matching_devices('*/vc/all')
    tp = VaccaProfilePlot()
    tp.setWindowTitle(cmps[0])
    tp.setModel(cmps[0])
    tp.show()
    app.exec_()
