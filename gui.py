# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(402, 369)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioRemove = QRadioButton(self.tab)
        self.radioRemove.setObjectName(u"radioRemove")

        self.verticalLayout_3.addWidget(self.radioRemove)

        self.radioMerg = QRadioButton(self.tab)
        self.radioMerg.setObjectName(u"radioMerg")

        self.verticalLayout_3.addWidget(self.radioMerg)

        self.radioTotal = QRadioButton(self.tab)
        self.radioTotal.setObjectName(u"radioTotal")

        self.verticalLayout_3.addWidget(self.radioTotal)

        self.buttonConnect = QPushButton(self.tab)
        self.buttonConnect.setObjectName(u"buttonConnect")

        self.verticalLayout_3.addWidget(self.buttonConnect)

        self.buttonRun = QPushButton(self.tab)
        self.buttonRun.setObjectName(u"buttonRun")

        self.verticalLayout_3.addWidget(self.buttonRun)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_5 = QVBoxLayout(self.tab_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.radioMil = QRadioButton(self.tab_2)
        self.radioMil.setObjectName(u"radioMil")

        self.horizontalLayout.addWidget(self.radioMil)

        self.radioMM = QRadioButton(self.tab_2)
        self.radioMM.setObjectName(u"radioMM")

        self.horizontalLayout.addWidget(self.radioMM)

        self.checkFlip = QCheckBox(self.tab_2)
        self.checkFlip.setObjectName(u"checkFlip")

        self.horizontalLayout.addWidget(self.checkFlip)


        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.editGap = QLineEdit(self.tab_2)
        self.editGap.setObjectName(u"editGap")

        self.gridLayout.addWidget(self.editGap, 1, 1, 1, 1)

        self.label_3 = QLabel(self.tab_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.editLength = QLineEdit(self.tab_2)
        self.editLength.setObjectName(u"editLength")

        self.gridLayout.addWidget(self.editLength, 2, 1, 1, 1)

        self.label_2 = QLabel(self.tab_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.editWidth = QLineEdit(self.tab_2)
        self.editWidth.setObjectName(u"editWidth")

        self.gridLayout.addWidget(self.editWidth, 0, 1, 1, 1)

        self.label = QLabel(self.tab_2)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.comboMode = QComboBox(self.tab_2)
        self.comboMode.setObjectName(u"comboMode")

        self.gridLayout.addWidget(self.comboMode, 3, 1, 1, 1)

        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout)

        self.label_4 = QLabel(self.tab_2)
        self.label_4.setObjectName(u"label_4")
        font = QFont()
        font.setBold(False)
        self.label_4.setFont(font)

        self.verticalLayout_4.addWidget(self.label_4)

        self.buttonBreakout = QPushButton(self.tab_2)
        self.buttonBreakout.setObjectName(u"buttonBreakout")

        self.verticalLayout_4.addWidget(self.buttonBreakout)


        self.verticalLayout_5.addLayout(self.verticalLayout_4)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout_3.addWidget(self.tabWidget, 1, 0, 1, 1)

        self.buttonClose = QPushButton(self.centralwidget)
        self.buttonClose.setObjectName(u"buttonClose")

        self.gridLayout_3.addWidget(self.buttonClose, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 402, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.radioRemove.setText(QCoreApplication.translate("MainWindow", u"Remove stubs track", None))
        self.radioMerg.setText(QCoreApplication.translate("MainWindow", u"Merging collinear tracks", None))
        self.radioTotal.setText(QCoreApplication.translate("MainWindow", u"Remove stubs track + Merging collinear tracks", None))
        self.buttonConnect.setText(QCoreApplication.translate("MainWindow", u"Connect to KiCad", None))
        self.buttonRun.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Track Optimizer", None))
        self.radioMil.setText(QCoreApplication.translate("MainWindow", u"mil", None))
        self.radioMM.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.checkFlip.setText(QCoreApplication.translate("MainWindow", u"Flip direction escape length", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Escape Length:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"DP Gap:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"DP Width:", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Escape Mode:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Please select exactly 2 pads before running this tool", None))
        self.buttonBreakout.setText(QCoreApplication.translate("MainWindow", u"Breakout Diff Pair", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Differential Pair", None))
        self.buttonClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
    # retranslateUi

