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
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(413, 325)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.buttonRun = QPushButton(self.centralwidget)
        self.buttonRun.setObjectName(u"buttonRun")
        self.buttonRun.setGeometry(QRect(280, 210, 94, 26))
        self.buttonConnect = QPushButton(self.centralwidget)
        self.buttonConnect.setObjectName(u"buttonConnect")
        self.buttonConnect.setGeometry(QRect(130, 210, 131, 26))
        self.buttonClose = QPushButton(self.centralwidget)
        self.buttonClose.setObjectName(u"buttonClose")
        self.buttonClose.setGeometry(QRect(20, 210, 94, 26))
        self.buttonColor = QPushButton(self.centralwidget)
        self.buttonColor.setObjectName(u"buttonColor")
        self.buttonColor.setGeometry(QRect(110, 140, 94, 26))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 413, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.buttonRun.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.buttonConnect.setText(QCoreApplication.translate("MainWindow", u"Connect to KiCad", None))
        self.buttonClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.buttonColor.setText(QCoreApplication.translate("MainWindow", u"Color", None))
    # retranslateUi

