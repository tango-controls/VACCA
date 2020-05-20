#!/usr/bin/env python

import taurus,traceback,sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
import fandango as fn
from math import ceil
from vacca.panel import VaccaAction

APPS = [
'jive',
'astor',
'ctarchiving',
'vacca',
'vaccagui',
'panic',
'tauruspanel',
'taurusdevicepanel',
'taurusdevtree',
'taurustrend',
'taurustrend2d',
'taurusform',
'taurusfinder',
'taurusgui',
]



app = TaurusApplication()

class VaccaBar(Qt.QWidget):
    
    TF = "--default-formatter=taurus.core.tango.util.tangoFormatter"
    
    def __init__(self,parent=None):
        Qt.QWidget.__init__(self, parent)
        self.setupUi()
        
    def setupUi(self):
        self.setLayout(Qt.QGridLayout())
        self.setWindowTitle('VACCA: Tango/Taurus Applications Launcher')
        self.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
        
        self.check = Qt.QCheckBox()
        self.check.setText('add tango formatter')

        self.args = Qt.QLineEdit("")

        self.cols = int(ceil(len(APPS)/2.))
        self.buttons = []
        
        self.resize(self.cols*200,150)
        ly = self.layout()
        ly.addWidget(self.check,2,self.cols-1)
        ly.addWidget(Qt.QLabel("arguments"),2,0)
        ly.addWidget(self.args,2,1,1,self.cols-2)
        
        self.check.clicked.connect(self.update_models)
        self.args.textChanged.connect(self.update_models)

        for j in range(2):
            for i in range(self.cols):
                try:
                    x = self.cols*j+i
                    if x>= len(APPS):
                        break

                    a = APPS[x]
                    b = VaccaAction(default=a)#Qt.QPushButton()
                    self.buttons.append(b)
                    b.setText(a)
                    b.setLogLevel(b.Warning)
                    ly.addWidget(b,j,i)
                    #b.clicked.connect(
                            ##b,Qt.SIGNAL("triggered()"),launch_app)
                            #(lambda v,o=b:launch_app(o)))
                except:
                    traceback.print_exc()
                    
        self.update_models()
            
    def update_models(self, *args):
        print('update_models')
        for b in self.buttons:
            app = str(b.text())
            c = ([self.TF] if self.check.isChecked() 
                            and a.startswith('taurus') else [])
            c.extend([str(a) for a in str(self.args.text()).strip().split()])
            b.setModel(c)
            b.setText(app)

    def launch_app(self, app=None):
        args = self.args
        try:
            print('launch_app(%s)'%app)
            if not fn.isString(app):
                if hasattr(app,'text'):
                    app = str(app.text()).strip()
                else:
                    app = str(app)
            print('launch_app(%s)'%app)
            args = str(args.text()).strip()
            #-hold
            app = "xterm -e %s" % app
            if check.isChecked():
                args = TF + " " + args
            c = "%s %s &" % (app,args)
            print('launch_app(%s)'%c)
            print('>'*80)
            fn.shell_command(c)
        except:
            traceback.print_exc()
    
if __name__ == '__main__':
    APPS.extend(sys.argv[1:])
    form = VaccaBar()
    form.show()
    app.exec_()
