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
    QFormLayout, QHBoxLayout, QHeaderView, QPushButton,
    QSizePolicy, QSpacerItem, QTreeView, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(634, 424)
        SettingsDialog.setSizeGripEnabled(False)
        SettingsDialog.setModal(True)
        self.formLayout = QFormLayout(SettingsDialog)
        self.formLayout.setObjectName(u"formLayout")
        self.tree_view = QTreeView(SettingsDialog)
        self.tree_view.setObjectName(u"tree_view")
        self.tree_view.setTabKeyNavigation(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.header().setCascadingSectionResizes(True)
        self.tree_view.header().setStretchLastSection(True)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.tree_view)

        self.button_box = QDialogButtonBox(SettingsDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.RestoreDefaults|QDialogButtonBox.StandardButton.Save)
        self.button_box.setCenterButtons(False)

        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.button_box)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.expand_button = QPushButton(SettingsDialog)
        self.expand_button.setObjectName(u"expand_button")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.expand_button.setIcon(icon)
        self.expand_button.setIconSize(QSize(8, 8))

        self.horizontalLayout.addWidget(self.expand_button)

        self.collapse_button = QPushButton(SettingsDialog)
        self.collapse_button.setObjectName(u"collapse_button")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoUp))
        self.collapse_button.setIcon(icon1)
        self.collapse_button.setIconSize(QSize(8, 8))

        self.horizontalLayout.addWidget(self.collapse_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.formLayout.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout)


        self.retranslateUi(SettingsDialog)
        self.button_box.accepted.connect(SettingsDialog.accept)
        self.button_box.rejected.connect(SettingsDialog.reject)
        self.expand_button.clicked.connect(self.tree_view.expandAll)
        self.collapse_button.clicked.connect(self.tree_view.collapseAll)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
        self.expand_button.setText("")
        self.collapse_button.setText("")
    # retranslateUi

