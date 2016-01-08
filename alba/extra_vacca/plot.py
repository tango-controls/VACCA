def setup_profile_plot(tp,gauges,pumps,tcs,positions=None,labels=None):
    """ This method configures a tau plot to show pressure/temperature profiles """
    
    from PyQt4 import Qwt5
    #tp.setModel('BO/VC/Composer/IPAxxis|BO/VC/Composer/IPPressures')
    #tp.setModel('BO/VC/Composer/CCGAxxis|BO/VC/Composer/CCGPressures,BO/VC/Composer/IPPressures')
    #positions = [0,17,31,33,49,63,80,94,111,114,116,122]
    #labels=['Q1A','Q1B','Q1LTB','Q2A','Q2B','Q3A','Q3B','Q4A','Q4B','Q4BT','Q4C','Q4D+RF']
    
    pumps,gauges,tcs = [str(s).lower() for s in (pumps,gauges,tcs)]
    tp.setModel(pumps)
    tp.addModels([tcs])
    tcs = tcs.split('|')[-1]
    tp.setCurvesYAxis([tcs],tp.yRight)
    tp.addModels([gauges])
    gauges = gauges.split('|')[-1]
    Curves = {}
    for cname in (pumps,gauges,tcs):
        try: Curves[cname] = tp.curves[cname]
        except: Curves[cname] = tp.curves[cname.split('|')[-1]]
        
    if positions and labels:
        try:
            positions = list(int(i) for i in TAU.Attribute(positions).read().value)
            labels = list(str(i) for i in TAU.Attribute(labels).read().value)
            tp.setAxisCustomLabels(Qwt5.QwtPlot.xBottom,zip(positions,labels),60)    
        except:
            print 'Unable to read pressure profile labels'
            print traceback.format_exc()
    
    for cname,color,width in [(gauges,Qt.Qt.blue,3),(pumps,Qt.Qt.magenta,1),(tcs,Qt.Qt.red,2)]:
        cap = Curves[cname].getAppearanceProperties()
        cap.lColor = color
        cap.lWidth = width
        tp.setCurveAppearanceProperties({Curves[cname].getCurveName():cap})
        
    Curves[gauges].setSymbol(Qwt5.QwtSymbol(Qwt5.QwtSymbol.Diamond,Qt.QBrush(Qt.Qt.yellow),Qt.QPen(Qt.Qt.green),Qt.QSize(7,7)))
    #f1 = Qwt5.QwtSplineCurveFitter()
    #f1.setSplineSize(2000)
    #Curves[pumps].setCurveFitter(f1)
    #Curves[pumps].setCurveAttribute(Curves[pumps].Fitted,True)
    tp.enableAxis(tp.yRight)        
    tp.setAxisScaleType(Qwt5.QwtPlot.yLeft,Qwt5.QwtScaleTransformation.Log10)
    tp.setAxisScale(Qwt5.QwtPlot.yLeft,1e-11,1e-6)
    tp.setCanvasBackground(Qt.Qt.white)
    tp.toggleDataInspectorMode(True)
    tp.showMaxPeaks(True)
    Curves[pumps].showMaxPeak(False)
    tp.setAllowZoomers(False)
    tp.toggleDataInspectorMode(True)
    tp.disconnect(tp._picker, Qt.SIGNAL('selected(QwtPolygon)'), tp.pickDataPoint)
    tp.connect(
        tp._picker, 
        Qt.SIGNAL('selected(QwtPolygon)'), 
        lambda pos,s=tp:pickPlotPoint(s,pos,xlabels=(zip(positions,labels) if positions and labels else None))
        )
    return tp    
    
def setup_pressure_trend(tt,models):
    from PyQt4 import Qwt5
    n,w = str(qtw.tabText(qtw.count()-1)),qtw.widget(qtw.count()-1)
    qtw.insertTab(0,w,n)
    tt.setXDynScale(True)
    xMax = time.time() #tt.axisScaleDiv(Qwt5.QwtPlot.xBottom).upperBound()
    #xMin = tt.axisScaleDiv(Qwt5.QwtPlot.xBottom).lowerBound()
    rg = 3600 #abs(self.str2deltatime(str(self.ui.xRangeCB.currentText())))
    xMin=xMax-rg
    tt.setAxisScale(Qwt5.QwtPlot.xBottom,xMin, xMax)
    tp.setAxisScaleType(Qwt5.QwtPlot.yLeft,Qwt5.QwtScaleTransformation.Log10)
    tp.setAxisScale(Qwt5.QwtPlot.yLeft,1e-11,1e-6)
    tp.setCurvesYAxis([tcs],tp.yRight)
    tt.addModels(models)
    
def pickPlotPoint(self, pos, scope=20, showMarker=True, targetCurveNames=None, xlabels=None):
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
    if isinstance(pos,Qt.QPolygon):pos=pos.first()
    scopeRect=Qt.QRect(0,0,scope,scope)
    scopeRect.moveCenter(pos)
    mindist=scope
    picked=None
    pickedCurveName=None
    pickedIndex=None
    self.curves_lock.acquire()
    try:
        if targetCurveNames is None: targetCurveNames = self.curves.iterkeys()
        for name in targetCurveNames:
            curve = self.curves.get(name, None)
            if curve is None: self.error("Curve '%s' not found"%name)
            if not curve.isVisible(): continue
            data=curve.data()
            for i in xrange(data.size()):
                point=Qt.QPoint(self.transform(curve.xAxis(),data.x(i)) , self.transform(curve.yAxis(),data.y(i)))
                if scopeRect.contains(point):
                    dist=(pos-point).manhattanLength()
                    if dist < mindist:
                        mindist=dist
                        picked = Qt.QPointF(data.x(i),data.y(i))
                        pickedCurveName=name
                        pickedIndex=i
                        pickedAxes = curve.xAxis(), curve.yAxis()
    finally:
        self.curves_lock.release()
    
    xlabels = xlabels or []
    print "pickPlotPoint(x=%s,y=%s,xlabels=[%s])"%(picked.x(),picked.y(),len(xlabels))

    if showMarker and picked is not None:
        self._pickedMarker.detach()
        self._pickedMarker.setValue(picked)
        self._pickedMarker.setAxis(*pickedAxes)
        self._pickedMarker.attach(self)
        self._pickedCurveName=pickedCurveName
        self._pickedMarker.pickedIndex=pickedIndex
        self.replot()
        label=self._pickedMarker.label()
        try: 
            xi,xl = ([(x[0],x[1]) for x in (xlabels or []) if x[0]<=picked.x()] or [-1,None])[-1]
            c = self.curves[pickedCurveName]
            #xc = [self.transform(c.xAxis(),x) for x in c.data().xData()]
            xc = [x for x in c.data().xData()]
            xx = len([x for x in xc if x>=xi and x<=picked.x()])
            #print [x[0] for x in xlabels]
            #print 'picked point: %s'%picked.x()
            #print 'last label %s at %s'%(xl,xi)
            #print 'data point are %s'%(xc)
            #print 'data points between pick and label: %s'%xx
            index=xx
        except: index,xl = (-1,None)
        if xl:
            infotxt = "'%s'[%i]:\n\t (%s-%02d,%.2e)"%(pickedCurveName,pickedIndex,xl,index,picked.y())
        elif self.getXIsTime():
            infotxt = "'%s'[%i]:\n\t (x=%s,%.3g)"%(pickedCurveName,pickedIndex,datetime.fromtimestamp(picked.x()).ctime(),picked.y())
        else:
            infotxt = "'%s'[%i]:\n\t (x=%.3g, y=%.3g)"%(pickedCurveName,pickedIndex,picked.x(),picked.y())
        label.setText(infotxt)
        print '\t%s'%infotxt
        fits = label.textSize().width()<self.size().width()
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
            popup.move(self.pos().x()-popup.size().width(),self.pos().y() )
            popup.move(self.pos())
            Qt.QTimer.singleShot(5000, popup.hide)
        
    return picked,pickedCurveName,pickedIndex