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
        self.button_box = QDialogButtonBox(SettingsDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.RestoreDefaults|QDialogButtonBox.StandardButton.Save)
        self.button_box.setCenterButtons(False)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.button_box)

        self.tree_view = QTreeView(SettingsDialog)
        self.tree_view.setObjectName(u"tree_view")
        self.tree_view.setTabKeyNavigation(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.header().setCascadingSectionResizes(True)
        self.tree_view.header().setStretchLastSection(True)

        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.tree_view)


        self.retranslateUi(SettingsDialog)
        self.button_box.accepted.connect(SettingsDialog.accept)
        self.button_box.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
    # retranslateUi

