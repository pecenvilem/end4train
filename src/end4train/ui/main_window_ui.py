# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDockWidget, QGroupBox,
    QHBoxLayout, QLabel, QLayout, QListView,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(932, 742)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.Computer))
        MainWindow.setWindowIcon(icon)
        MainWindow.setDockNestingEnabled(True)
        MainWindow.setDockOptions(QMainWindow.DockOption.AllowNestedDocks|QMainWindow.DockOption.AllowTabbedDocks|QMainWindow.DockOption.AnimatedDocks|QMainWindow.DockOption.GroupedDragging)
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionPlot = QAction(MainWindow)
        self.actionPlot.setObjectName(u"actionPlot")
        self.actionPlot.setCheckable(True)
        self.actionPlot.setChecked(True)
        self.actionMap = QAction(MainWindow)
        self.actionMap.setObjectName(u"actionMap")
        self.actionMap.setCheckable(True)
        self.actionMap.setChecked(True)
        self.actionReset_Layout = QAction(MainWindow)
        self.actionReset_Layout.setObjectName(u"actionReset_Layout")
        self.actionOpen_log = QAction(MainWindow)
        self.actionOpen_log.setObjectName(u"actionOpen_log")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.actionOpen_log.setIcon(icon1)
        self.actionSave_Layout = QAction(MainWindow)
        self.actionSave_Layout.setObjectName(u"actionSave_Layout")
        self.actionVista = QAction(MainWindow)
        self.actionVista.setObjectName(u"actionVista")
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.actionSettings.setIcon(icon2)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setAutoFillBackground(False)
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.hot_btn = QRadioButton(self.groupBox)
        self.hot_btn.setObjectName(u"hot_btn")
        self.hot_btn.setChecked(True)

        self.horizontalLayout.addWidget(self.hot_btn)

        self.eot_btn = QRadioButton(self.groupBox)
        self.eot_btn.setObjectName(u"eot_btn")

        self.horizontalLayout.addWidget(self.eot_btn)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.record_box = QCheckBox(self.groupBox)
        self.record_box.setObjectName(u"record_box")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.record_box.sizePolicy().hasHeightForWidth())
        self.record_box.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.record_box)


        self.verticalLayout_7.addLayout(self.verticalLayout)


        self.verticalLayout_8.addWidget(self.groupBox)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_6.addWidget(self.label_3)

        self.traces_list_view = QListView(self.centralwidget)
        self.traces_list_view.setObjectName(u"traces_list_view")

        self.verticalLayout_6.addWidget(self.traces_list_view)


        self.verticalLayout_8.addLayout(self.verticalLayout_6)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.load_btn = QPushButton(self.groupBox_3)
        self.load_btn.setObjectName(u"load_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.load_btn.sizePolicy().hasHeightForWidth())
        self.load_btn.setSizePolicy(sizePolicy1)

        self.verticalLayout_5.addWidget(self.load_btn)

        self.open_btn = QPushButton(self.groupBox_3)
        self.open_btn.setObjectName(u"open_btn")
        sizePolicy1.setHeightForWidth(self.open_btn.sizePolicy().hasHeightForWidth())
        self.open_btn.setSizePolicy(sizePolicy1)

        self.verticalLayout_5.addWidget(self.open_btn)


        self.verticalLayout_8.addWidget(self.groupBox_3)


        self.horizontalLayout_2.addLayout(self.verticalLayout_8)

        self.gauges_group_box = QGroupBox(self.centralwidget)
        self.gauges_group_box.setObjectName(u"gauges_group_box")

        self.horizontalLayout_2.addWidget(self.gauges_group_box)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 932, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuWindow = QMenu(self.menuBar)
        self.menuWindow.setObjectName(u"menuWindow")
        MainWindow.setMenuBar(self.menuBar)
        self.dock_plot = QDockWidget(MainWindow)
        self.dock_plot.setObjectName(u"dock_plot")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.plot = GraphicsLayoutWidget(self.dockWidgetContents_2)
        self.plot.setObjectName(u"plot")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.plot.sizePolicy().hasHeightForWidth())
        self.plot.setSizePolicy(sizePolicy2)
        self.plot.setMinimumSize(QSize(400, 200))

        self.verticalLayout_3.addWidget(self.plot)

        self.dock_plot.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_plot)
        self.dock_map = QDockWidget(MainWindow)
        self.dock_map.setObjectName(u"dock_map")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.map = QQuickWidget(self.dockWidgetContents_3)
        self.map.setObjectName(u"map")
        sizePolicy2.setHeightForWidth(self.map.sizePolicy().hasHeightForWidth())
        self.map.setSizePolicy(sizePolicy2)
        self.map.setMinimumSize(QSize(400, 200))
        self.map.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)

        self.verticalLayout_4.addWidget(self.map)

        self.dock_map.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_map)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuWindow.menuAction())
        self.menuFile.addAction(self.actionOpen_log)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuWindow.addAction(self.actionPlot)
        self.menuWindow.addAction(self.actionMap)
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.actionSave_Layout)
        self.menuWindow.addAction(self.actionReset_Layout)

        self.retranslateUi(MainWindow)
        self.actionMap.triggered["bool"].connect(self.dock_map.setVisible)
        self.actionPlot.triggered["bool"].connect(self.dock_plot.setVisible)
        self.dock_map.visibilityChanged.connect(self.actionMap.setChecked)
        self.dock_plot.visibilityChanged.connect(self.actionPlot.setChecked)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"TIMS monitor", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionPlot.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
#if QT_CONFIG(shortcut)
        self.actionPlot.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionMap.setText(QCoreApplication.translate("MainWindow", u"Map", None))
#if QT_CONFIG(shortcut)
        self.actionMap.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+M", None))
#endif // QT_CONFIG(shortcut)
        self.actionReset_Layout.setText(QCoreApplication.translate("MainWindow", u"Restore Layout", None))
#if QT_CONFIG(shortcut)
        self.actionReset_Layout.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_log.setText(QCoreApplication.translate("MainWindow", u"Open log", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_log.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_Layout.setText(QCoreApplication.translate("MainWindow", u"Save Layout", None))
        self.actionVista.setText(QCoreApplication.translate("MainWindow", u"Vista", None))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
#if QT_CONFIG(shortcut)
        self.actionSettings.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+K", None))
#endif // QT_CONFIG(shortcut)
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Data source:", None))
        self.hot_btn.setText(QCoreApplication.translate("MainWindow", u"HoT", None))
        self.eot_btn.setText(QCoreApplication.translate("MainWindow", u"EoT", None))
        self.record_box.setText(QCoreApplication.translate("MainWindow", u"Record on-line", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Select traces:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Log", None))
        self.load_btn.setText(QCoreApplication.translate("MainWindow", u"Download", None))
        self.open_btn.setText(QCoreApplication.translate("MainWindow", u"Open file", None))
        self.gauges_group_box.setTitle(QCoreApplication.translate("MainWindow", u"Current values", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuWindow.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.dock_plot.setWindowTitle(QCoreApplication.translate("MainWindow", u"Plot", None))
        self.dock_map.setWindowTitle(QCoreApplication.translate("MainWindow", u"Map", None))
    # retranslateUi

