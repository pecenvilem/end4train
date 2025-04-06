# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QHeaderView, QSizePolicy, QTreeView,
    QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(403, 201)
        SettingsDialog.setSizeGripEnabled(False)
        SettingsDialog.setModal(True)
        self.formLayout = QFormLayout(SettingsDialog)
        self.formLayout.setObjectName(u"formLayout")
        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.RestoreDefaults|QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setCenterButtons(False)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.buttonBox)

        self.treeView = QTreeView(SettingsDialog)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setTabKeyNavigation(True)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.header().setCascadingSectionResizes(True)
        self.treeView.header().setStretchLastSection(False)

        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.treeView)


        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
    # retranslateUi

