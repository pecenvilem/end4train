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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(215, 98)
        SettingsDialog.setSizeGripEnabled(False)
        SettingsDialog.setModal(False)
        self.formLayout = QFormLayout(SettingsDialog)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(SettingsDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.style_combobox = QComboBox(SettingsDialog)
        self.style_combobox.setObjectName(u"style_combobox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.style_combobox)

        self.label_2 = QLabel(SettingsDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.color_override_combobox = QComboBox(SettingsDialog)
        self.color_override_combobox.addItem("")
        self.color_override_combobox.addItem("")
        self.color_override_combobox.addItem("")
        self.color_override_combobox.setObjectName(u"color_override_combobox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.color_override_combobox)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setCenterButtons(False)

        self.formLayout.setWidget(2, QFormLayout.SpanningRole, self.buttonBox)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.style_combobox)
        self.label_2.setBuddy(self.color_override_combobox)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Style", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Override Color Scheme", None))
        self.color_override_combobox.setItemText(0, QCoreApplication.translate("SettingsDialog", u"None", None))
        self.color_override_combobox.setItemText(1, QCoreApplication.translate("SettingsDialog", u"Light", None))
        self.color_override_combobox.setItemText(2, QCoreApplication.translate("SettingsDialog", u"Dark", None))

    # retranslateUi

