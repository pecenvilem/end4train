# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'monitor_main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QListView, QMainWindow,
    QMenu, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSplitter, QStatusBar,
    QTableView, QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1007, 718)
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setAutoFillBackground(False)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.hot_btn = QRadioButton(self.groupBox)
        self.hot_btn.setObjectName(u"hot_btn")
        self.hot_btn.setChecked(True)

        self.horizontalLayout.addWidget(self.hot_btn)

        self.eot_btn = QRadioButton(self.groupBox)
        self.eot_btn.setObjectName(u"eot_btn")

        self.horizontalLayout.addWidget(self.eot_btn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_6.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.record_box = QCheckBox(self.groupBox_2)
        self.record_box.setObjectName(u"record_box")

        self.verticalLayout.addWidget(self.record_box)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.traces_list_view = QListView(self.groupBox_2)
        self.traces_list_view.setObjectName(u"traces_list_view")

        self.verticalLayout.addWidget(self.traces_list_view)

        self.groupBox_3 = QGroupBox(self.groupBox_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.load_btn = QPushButton(self.groupBox_3)
        self.load_btn.setObjectName(u"load_btn")

        self.verticalLayout_5.addWidget(self.load_btn)

        self.open_btn = QPushButton(self.groupBox_3)
        self.open_btn.setObjectName(u"open_btn")

        self.verticalLayout_5.addWidget(self.open_btn)


        self.verticalLayout.addWidget(self.groupBox_3)


        self.verticalLayout_6.addWidget(self.groupBox_2)


        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_2.setOpaqueResize(True)
        self.splitter_2.setChildrenCollapsible(True)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.table = QTableView(self.widget)
        self.table.setObjectName(u"table")

        self.verticalLayout_2.addWidget(self.table)

        self.splitter.addWidget(self.widget)
        self.widget1 = QWidget(self.splitter)
        self.widget1.setObjectName(u"widget1")
        self.verticalLayout_3 = QVBoxLayout(self.widget1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.widget1)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.map = QQuickWidget(self.widget1)
        self.map.setObjectName(u"map")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map.sizePolicy().hasHeightForWidth())
        self.map.setSizePolicy(sizePolicy)
        self.map.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)

        self.verticalLayout_3.addWidget(self.map)

        self.splitter.addWidget(self.widget1)
        self.splitter_2.addWidget(self.splitter)
        self.widget2 = QWidget(self.splitter_2)
        self.widget2.setObjectName(u"widget2")
        self.verticalLayout_4 = QVBoxLayout(self.widget2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget2)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.plot = GraphicsLayoutWidget(self.widget2)
        self.plot.setObjectName(u"plot")

        self.verticalLayout_4.addWidget(self.plot)

        self.splitter_2.addWidget(self.widget2)

        self.horizontalLayout_2.addWidget(self.splitter_2)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1007, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionClose)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"TIMS monitor", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Data source:", None))
        self.hot_btn.setText(QCoreApplication.translate("MainWindow", u"HoT", None))
        self.eot_btn.setText(QCoreApplication.translate("MainWindow", u"EoT", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Controls", None))
        self.record_box.setText(QCoreApplication.translate("MainWindow", u"Record on-line", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Select traces", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Log", None))
        self.load_btn.setText(QCoreApplication.translate("MainWindow", u"Download", None))
        self.open_btn.setText(QCoreApplication.translate("MainWindow", u"Open file", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Data", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Map", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

