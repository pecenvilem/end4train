from __future__ import annotations
import sys
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import Iterable, Any, Type, Annotated, Callable
import faulthandler

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from PySide6.QtWidgets import QApplication, QTreeView, QStyledItemDelegate, QWidget, QComboBox, QStyleFactory, \
    QDoubleSpinBox, QLineEdit, QSpinBox, QCheckBox, QStyleOptionProgressBar
from pydantic import BaseModel, Field, AfterValidator


def drop_duplicates(original: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(original))


def split_levels(key: str) -> list[str]:
    return key.split("/")


class TestEnum(Enum):
    VALUE_ONE = 1
    VALUE_TWO = "2"
    VALUE_THREE = ["t", "h", "r", "e", "e"]

@dataclass
class SettingsKeyDetail:
    key: str
    presentation_name: str


class Key(Enum):
    THEME = SettingsKeyDetail("theme", "Theme")
    STYLE = SettingsKeyDetail("style", "Style")
    COLOR_SCHEME = SettingsKeyDetail("colorScheme", "Color Scheme")

    @classmethod
    @lru_cache
    def get_presentation(cls, key: str) -> str | None:
        for item in cls:
            if item.value.key == key:
                return item.value.presentation_name

def validate_style_string(style_string: str, style_factory:Callable[[], list[str]] = QStyleFactory.keys) -> str:
    allowed = style_factory()
    if style_string not in allowed:
        raise ValueError(f"Can't create QStyle for factory string: {style_string}")
    return style_string

class PressureGaugeWidget(BaseModel):
    min_value: float = Annotated[0.0, Field(alias="minValue", title="Minimum value")]
    max_value: float = Annotated[12.0, Field(alias="maxValue", title="Maximum value")]
    min_angle: float = Annotated[10.0, Field(alias="minAngle", title="Minimum angle")]
    max_angle: float = Annotated[350.0, Field(alias="maxAngle", title="Maximum angle")]
    major_tick_count: int = Annotated[6, Field(alias="majorTickCount", title="Major ticks over the gauge range")]
    minor_tick_count: int = Annotated[5, Field(alias="minorTickCount", title="Minor ticks between two major ticks")]
    minor_tick_labels: bool = Annotated[False, Field(alias="minorTickLabels", title="Labels on minor ticks")]

def pressure_gauge_widget_factory(
        min_value: float, max_value: float, max_angle: float, min_angle: float,
        major_tick_count: int, minor_tick_count: int, minor_tick_labels: bool
) -> PressureGaugeWidget:
    return PressureGaugeWidget(
        min_value=min_value, max_value=max_value, min_angle=min_angle, max_angle=max_angle,
        major_tick_count=major_tick_count, minor_tick_count=minor_tick_count, minor_tick_labels=minor_tick_labels
    )

class ThemeSection(BaseModel):
    style: str = Annotated["windows11", AfterValidator(validate_style_string)]
    color_scheme: Qt.ColorScheme = Annotated[Qt.ColorScheme.Unknown, Field(alias="colorScheme", title="Color Scheme")]

class PressureWidgetSection(BaseModel):
    main_reservoir: PressureGaugeWidget = Annotated[
        pressure_gauge_widget_factory(0.0, 12.0, 10, 350, 6, 5, False),
        Field(alias="mainReservoir", title="Main reservoir")
    ]

class WidgetSection(BaseModel):
    pressure_widgets: PressureWidgetSection = Annotated[
        PressureWidgetSection(),
        Field(alias="pressureWidgets", title="Pressure gauges")
    ]

class Settings(BaseModel):
    autostart: bool = Annotated[False, Field(title="Autostart")]
    theme: ThemeSection = Annotated[ThemeSection(), Field(title="Theme")]
    widget: WidgetSection = Annotated[WidgetSection(), Field(title="Widgets")]

# TODO: try to init an instance of Settings and serialize it into a JSON file
# TODO: create JSON schema for Settings


@dataclass
class SettingsNode:
    path: str = "/"
    parent: SettingsNode | None = None
    children: dict[str, SettingsNode] = field(default_factory=dict)
    value: Any = None

    def __post_init__(self) -> None:
        self.stem = split_levels(self.path)[-1]


class SettingsModel(QAbstractItemModel):

    # TODO: create a function, which builds a tree of SettingsNodes from Settings object

    def __init__(self, settings_data: dict, parent: QObject | None = None):
        super().__init__(parent)
        self._headers = ("key", "value")
        self.root_node = SettingsModel.build_tree(settings_data)
        self.settings = Settings()
        pass

    @staticmethod
    def build_tree(settings: dict) -> SettingsNode:
        root = SettingsNode()
        for key, value in settings.items():
            levels = split_levels(key)
            parent = root
            path = ""
            for i, level in enumerate(levels):
                path = f"{path}/{level}"
                if path not in parent.children:
                    node = SettingsNode(path, parent, {}, value if i+1 == len(levels) else None)
                    parent.children[path] = node
                parent = parent.children[path]
        return root

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        node: SettingsNode = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                presentation = Key.get_presentation(node.stem)
                if presentation is not None:
                    return presentation
                return node.stem
            elif index.column() == 1:
                return node.value
        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return node.value

    def setData(self, index, value, /, role = ...):
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                node: SettingsNode = index.internalPointer()
                node.value = str(value)
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
        child_key = list(parent_node.children)[row]
        child_node = parent_node.children[child_key]
        return self.createIndex(row, column, child_node)

    @lru_cache
    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        node: SettingsNode = index.internalPointer()
        parent_node = node.parent
        if parent_node == self.root_node:
            return QModelIndex()
        path = node.path
        parent_index = list(parent_node.children).index(path)
        return self.createIndex(parent_index, 0, parent_node)

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
        if index.column() == 1:
            return Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags


# TODO: instead of subclassing a delegate, try to find a way to supply a custom
#  itemEditorFactory function to the default QStyledItemDelegate
#  but this may not take care of setting model- and editor-data...
class Delegate(QStyledItemDelegate):

    BOUNDS = {
        "widget/pressureGauge/minLineAngle": 10,
        "widget/pressureGauge/maxLineAngle": 350,
        "widget/pressureGauge/majorTickCount": 6,
        "widget/pressureGauge/minorTickCount": 5,
        "widget/pressureGauge/minorTickLabels": False,
    }

    @staticmethod
    def get_value_list_override(key: Key) -> list[str] | None:
        mapping = {
            Key.STYLE: lambda: list(style.capitalize() for style in QStyleFactory.keys())
        }
        if key not in mapping:
            return None
        return mapping[key]()


    # TODO: implement...
    def createEditor(self, parent, option, index, /) -> QWidget:
        settings_node: SettingsNode = index.internalPointer()
        if isinstance(settings_node.value, Enum):
            combobox = QComboBox(parent)
            enum_class: Type[Enum] = type(settings_node.value)
            combobox.addItems([item.name for item in enum_class])
            return combobox
        if isinstance(settings_node.value, float):
            return QDoubleSpinBox(parent)
        # TODO: implement CheckBox for boolean values (requires reimplementing Delegate.paint)
        if isinstance(settings_node.value, bool):
            combobox = QComboBox(parent)
            combobox.addItems(["True", "False"])
            return combobox
        if isinstance(settings_node.value, int):
            return QSpinBox(parent)
        return QLineEdit(parent)

    # TODO: implement...
    def setEditorData(self, editor, index, /):
        pass
        # editor.insertItems(0, ["1", "2", index.internalPointer().value])

    # TODO: implement...
    def setModelData(self, editor, model, index, /):
        pass


def main() -> None:
    # TODO: use SettingsModel in SettingDialog

    settings_data = {
        "autostart": False, 
        "theme/style": "windows11",
        "theme/colorScheme": Qt.ColorScheme.Light,
        "widget/pressureGauge/minValue": 0.0,
        "widget/pressureGauge/maxValue": 12.0,
        "widget/pressureGauge/minLineAngle": 10,
        "widget/pressureGauge/maxLineAngle": 350,
        "widget/pressureGauge/majorTickCount": 6,
        "widget/pressureGauge/minorTickCount": 5,
        "widget/pressureGauge/minorTickLabels": False,
    }
    app = QApplication(sys.argv)
    tree_view = QTreeView()
    delegate = Delegate()
    tree_view.setItemDelegate(delegate)
    model = SettingsModel(settings_data)
    tree_view.setModel(model)
    tree_view.show()
    app.exec()


if __name__ == "__main__":
    faulthandler.enable()
    main()
