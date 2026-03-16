from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QTimer
from gui import Ui_MainWindow
from kicad_pcb import KiCadPCB
from version import version
from pcbsvg import PCBSVG

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Layer SVG v{version}")
        self.pcb = KiCadPCB()

        QTimer.singleShot(500, self.connect_kicad)
        self.ui.buttonClose.clicked.connect(self.close)
        self.ui.buttonConnect.clicked.connect(self.connect_kicad)
        self.ui.buttonRun.clicked.connect(self.button_run_clicked)
        self.ui.buttonColor.clicked.connect(self.button_color_clicked)
    
    def connect_kicad(self):
        connected, status = self.pcb.connect_kicad()
        if connected:
            self.ui.statusbar.showMessage(f"Connected to KiCad {self.pcb.kicad.get_version()}")
        else:
            self.ui.statusbar.showMessage(status)
            QMessageBox.information(self, "Message", status)

    def button_run_clicked(self):
        status = self.pcb.get_data()
        if status == False:
            QMessageBox.information(self, "Message", "Please add Edge Cuts")
            return
        PCBSVG(self.pcb)
        print("Done")
    
    def button_color_clicked(self):
        #PCBSVG(self.pcb)
        print("Done")