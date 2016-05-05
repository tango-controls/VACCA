
import tau
from tau.widget import Qt

if __name__ == "__main__":
    import sys
    tau.setLogLevel(tau.Debug)
    app = Qt.QApplication(sys.argv)
    
    #form = QtGui.QDialog()
    #ly=QtGui.QVBoxLayout(form)
    #container=QtGui.QWidget()
    #ly.addWidget(container)   
    #for m in sys.argv[1:]:
        #tv=TauJDrawSynopticsView(container, designMode=False)
        #tv.setModel(m)
        
    form = tau.widget.TauJDrawSynopticsView(designMode=False)
    form.setAlias({'#':'BO01/VC/'})
    form.setModel(sys.argv[1])
    form.scene().setSelectionMark('image/icons/info.png',20,20)
    print 'SizeHint for %s is: %s' %(sys.argv[1],form.sizeHint())
    
    def kk(*args):print "!!!!!!!!!", args
    form.connect(form,Qt.SIGNAL("graphicItemSelected(QString)"), kk)
    
    SCROLL_BARS_WORK_PROPERLY = True
    if SCROLL_BARS_WORK_PROPERLY:
        panel = Qt.QFrame()
        layout = Qt.QGridLayout()
        layout.addWidget(form)        
        panel.setLayout(layout)    
        panel.show()
        print 'form.size is %s, panel size is %s' % (form.size(),panel.size())
    else:
        form.show()
    
    sys.exit(app.exec_())
