from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Type, Annotated, Callable

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QComboBox, QStyleFactory, \
    QDoubleSpinBox, QLineEdit, QSpinBox, QCheckBox, QStyleOption, QStyleOptionViewItem
from annotated_types import Ge, Gt, Le, Lt
from pydantic import BaseModel, Field, AfterValidator
from pydantic.fields import FieldInfo


def validate_style_string(style_string: str, style_factory:Callable[[], list[str]] = QStyleFactory.keys) -> str:
    allowed = style_factory()
    if style_string not in allowed:
        raise ValueError(f"Can't create QStyle for factory string: {style_string}")
    return style_string

class PressureGaugeWidget(BaseModel):
    min_value: Annotated[float, Field(alias="minValue", title="Minimum value")] = 0.0
    max_value: Annotated[float, Field(alias="maxValue", title="Maximum value")] = 12.0
    min_angle: Annotated[float, Field(alias="minAngle", title="Minimum angle")] = 10.0
    max_angle: Annotated[float, Field(alias="maxAngle", title="Maximum angle")] = 350.0
    major_tick_count: Annotated[int, Field(alias="majorTickCount", title="Major ticks over the gauge range", ge=0)] = 6
    minor_tick_count: Annotated[int, Field(alias="minorTickCount", title="Minor ticks between two major ticks")] = 5
    minor_tick_labels: Annotated[bool, Field(alias="minorTickLabels", title="Labels on minor ticks")] = False

def pressure_gauge_widget_factory(
        min_value: float, max_value: float, max_angle: float, min_angle: float,
        major_tick_count: int, minor_tick_count: int, minor_tick_labels: bool
) -> PressureGaugeWidget:
    return PressureGaugeWidget(
        min_value=min_value, max_value=max_value, min_angle=min_angle, max_angle=max_angle,
        major_tick_count=major_tick_count, minor_tick_count=minor_tick_count, minor_tick_labels=minor_tick_labels
    )

class ThemeSection(BaseModel):
    style: Annotated[str, Field(title="Style"), AfterValidator(validate_style_string)] = "windows11"
    color_scheme: Annotated[Qt.ColorScheme, Field(alias="colorScheme", title="Color Scheme")] = Qt.ColorScheme.Unknown

class PressureWidgetSection(BaseModel):
    main_reservoir: Annotated[
        PressureGaugeWidget, Field(alias="mainReservoir", title="Main reservoir")
    ] = pressure_gauge_widget_factory(0.0, 12.0, 10, 350, 6, 5, False)

class WidgetSection(BaseModel):
    pressure_widgets: Annotated[
        PressureWidgetSection, Field(alias="pressureWidgets", title="Pressure gauges")
    ] = PressureWidgetSection()

class Settings(BaseModel):
    autostart: Annotated[bool, Field(title="Autostart")] = False
    theme: Annotated[ThemeSection, Field(title="Theme")] = ThemeSection()
    widget: Annotated[WidgetSection, Field(title="Widgets")] = WidgetSection()


type SettingsPath = tuple[str, ...]

class SettingsModel(QAbstractItemModel):

    @dataclass
    class Node:
        path: SettingsPath
        parent: SettingsModel.Node | None
        children: list[SettingsModel.Node]
        value: Any
        field_info: FieldInfo | None

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._headers = ("key", "value")
        self.settings = Settings()
        self.root_node = self.build_tree()
        pass

    def build_tree(self) -> SettingsModel.Node:
        root = SettingsModel.Node(
            path=tuple(), parent=None, children=list(), value=self.settings, field_info=None
        )
        remaining_nodes = [root]
        while remaining_nodes:
            current_node = remaining_nodes.pop()
            value = self.get_field_value(current_node.path)
            if not isinstance(value, BaseModel):
                continue
            value_model = type(value)
            current_node.children = list(
                SettingsModel.Node(
                    path=current_node.path + (stem, ), parent=current_node, children=list(),
                    value=self.get_field_value(current_node.path + (stem, )),
                    field_info=self.get_field_info(current_node.path + (stem,))
                )
                for stem in value_model.model_fields.keys()
            )
            remaining_nodes.extend(current_node.children)
        return root

    def get_field_value(self, path: SettingsPath) -> Any:
        current_object = self.settings
        try:
            for step in path:
                current_object = getattr(current_object, step)
        except AttributeError as e:
            raise ValueError(f"Invalid settings path: {path}") from e
        return current_object

    def set_field_value(self, path: SettingsPath, value: Any) -> None:
        parent = self.get_field_value(path[:-1])
        try:
            setattr(parent, path[-1], value)
        except AttributeError as e:
            raise ValueError(f"Invalid settings path: {path}") from e

    def get_field_info(self, path: SettingsPath) -> FieldInfo:
        parent: type[BaseModel] = type(self.get_field_value(path[:-1]))
        try:
            return parent.model_fields[path[-1]]
        except AttributeError as e:
            raise
        except KeyError as e:
            raise ValueError(f"Invalid settings path: {path}") from e

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        node: SettingsModel.Node = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                info = self.get_field_info(node.path)
                return info.title
            elif index.column() == 1:
                if issubclass(node.field_info.annotation, Enum):
                    return self.get_field_value(node.path).name
                return self.get_field_value(node.path)
        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return self.get_field_value(node.path)
        return None

    def setData(self, index, value, /, role = ...):
        # TODO: validate
        if role == Qt.ItemDataRole.EditRole:
            if index.column() != 1:
                return False
            node = index.internalPointer()
            self.set_field_value(node.path, value)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
            return True
        return False

    @lru_cache
    def headerData(self, section, orientation, /, role = ...):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    @lru_cache
    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_node = parent.internalPointer() if parent.isValid() else self.root_node
        return self.createIndex(row, column, parent_node.children[row])

    @lru_cache
    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        current_index_node: SettingsModel.Node = index.internalPointer()
        if current_index_node.parent == self.root_node:
            return QModelIndex()
        parent_row = current_index_node.parent.children.index(current_index_node)
        return self.createIndex(parent_row, 0, current_index_node.parent)

    @lru_cache
    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()
        return len(parent_node.children)

    @lru_cache
    def columnCount(self, parent: QModelIndex = ...):
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.column() == 1 and not index.internalPointer().children:
            return Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags


class Delegate(QStyledItemDelegate):

    @staticmethod
    def configure_spin_box(spinbox: QSpinBox | QDoubleSpinBox, metadata: list[Any]) -> QSpinBox:
        for constraint in metadata:
            try:
                if isinstance(constraint, Ge):
                    # noinspection PyTypeChecker
                    spinbox.setMinimum(constraint.ge)
                if isinstance(constraint, Gt):
                    # noinspection PyTypeChecker
                    spinbox.setMinimum(constraint.gt + 1)
                if isinstance(constraint, Le):
                    # noinspection PyTypeChecker
                    spinbox.setMaximum(constraint.le)
                if isinstance(constraint, Lt):
                    # noinspection PyTypeChecker
                    spinbox.setMaximum(constraint.lt - 1)
            except TypeError:
                continue
        return spinbox

    # TODO: implement...
    def createEditor(self, parent, option, index, /) -> QWidget:
        settings_node: SettingsModel.Node = index.internalPointer()

        if settings_node.field_info.annotation == bool:
            widget = QComboBox(parent, editable=False)
            widget.addItem(self.tr("true"), True)
            widget.addItem(self.tr("false"), False)
            return widget

        if settings_node.field_info.annotation == int:
            return self.configure_spin_box(
                QSpinBox(parent), settings_node.field_info.metadata
            )

        if settings_node.field_info.annotation == float:
            return self.configure_spin_box(
                QDoubleSpinBox(parent), settings_node.field_info.metadata
            )

        if issubclass(settings_node.field_info.annotation, Enum):
            widget = QComboBox(parent, editable=False)
            for member in settings_node.field_info.annotation:
                widget.addItem(member.name, member)
            return widget

        return super().createEditor(parent, option, index)

    def paint(self, painter, option, index, /):
        # TODO: add visualization using a QCheckBox for boolean values
        #  this will require reimplementing the checkbox behavior (style change on mouse hover, signals...) -> postponed
        #  example: https://stackoverflow.com/questions/59202334/python-pyqt5-is-it-possible-to-add-a-button-to-press-inside-qtreeview
        super().paint(painter, option, index)

    # TODO: validate...
    def setEditorData(self, editor, index, /):
        if isinstance(editor, QSpinBox):
            editor.setValue(index.data(Qt.ItemDataRole.EditRole))
            return

        if isinstance(editor, QDoubleSpinBox):
            editor.setValue(index.data(Qt.ItemDataRole.EditRole))
            return

        if isinstance(editor, QComboBox):
            editor.setCurrentIndex(
                editor.findData(index.data(Qt.ItemDataRole.EditRole))
            )
            return

        if isinstance(editor, QLineEdit):
            editor.setText(index.data(Qt.ItemDataRole.EditRole))
            return

    # TODO: implement...
    def setModelData(self, editor, model, index, /):
        pass
