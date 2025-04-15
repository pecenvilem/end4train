from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Type, Annotated, Callable

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QComboBox, QStyleFactory, \
    QDoubleSpinBox, QLineEdit, QSpinBox, QCheckBox
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
    major_tick_count: Annotated[int, Field(alias="majorTickCount", title="Major ticks over the gauge range")] = 6
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
        type_info: FieldInfo | None

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._headers = ("key", "value")
        self.settings = Settings()
        self.root_node = self.build_tree()
        pass

    def build_tree(self) -> SettingsModel.Node:
        root = SettingsModel.Node(
            path=tuple(), parent=None, children=list(), value=self.settings, type_info=None
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
                    type_info=self.get_field_info(current_node.path + (stem, ))
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
                return self.get_field_value(node.path)
        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return self.get_field_value(node.path)

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


# TODO: instead of subclassing a delegate, try to find a way to supply a custom
#  itemEditorFactory function to the default QStyledItemDelegate
#  but this may not take care of setting model- and editor-data...
class Delegate(QStyledItemDelegate):

    # TODO: implement...
    def createEditor(self, parent, option, index, /) -> QWidget:
        widget_map: dict[type, Type[QWidget]] = {
            bool: QCheckBox,
            int: QSpinBox,
            float: QDoubleSpinBox,
            Enum: QComboBox
        }
        settings_node: SettingsModel.Node = index.internalPointer()
        widget_class = widget_map.get(settings_node.type_info.annotation, QLineEdit)

        # TODO: implement CheckBox for boolean values (requires reimplementing Delegate.paint)

        return widget_class(parent)

    # TODO: implement...
    def setEditorData(self, editor, index, /):
        pass
        # editor.insertItems(0, ["1", "2", index.internalPointer().value])

    # TODO: implement...
    def setModelData(self, editor, model, index, /):
        pass
