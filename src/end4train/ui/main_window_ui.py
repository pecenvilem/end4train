# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'monitor_main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QListView, QMainWindow,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTableView, QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
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

        self.horizontalSpacer = QSpacerItem(262, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addWidget(self.groupBox)

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


        self.verticalLayout_3.addWidget(self.groupBox_2)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.table_view = QTableView(self.centralwidget)
        self.table_view.setObjectName(u"table_view")

        self.verticalLayout_2.addWidget(self.table_view)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.chart_view = GraphicsLayoutWidget(self.centralwidget)
        self.chart_view.setObjectName(u"chart_view")

        self.verticalLayout_4.addWidget(self.chart_view)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 10)
        self.horizontalLayout_2.setStretch(2, 15)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"TIMS monitor", None))
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
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
    # retranslateUi

