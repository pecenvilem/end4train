from __future__ import annotations
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable, Any
import faulthandler

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from PySide6.QtWidgets import QApplication, QTreeView, QStyledItemDelegate, QWidget, QComboBox


def drop_duplicates(original: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(original))


def split_levels(key: str) -> list[str]:
    return key.split("/")


@dataclass
class SettingsNode:
    path: str = "/"
    parent: SettingsNode | None = None
    children: dict[str, SettingsNode] = field(default_factory=dict)

    value: Any = None
    def __post_init__(self) -> None:
        self.stem = split_levels(self.path)[-1]


class SettingsModel(QAbstractItemModel):
    def __init__(self, settings_data: dict, parent: QObject | None = None):
        super().__init__(parent)
        self._headers = ("key", "value")
        self.root_node = SettingsModel.build_tree(settings_data)

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
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super().flags(index)

        if index.column() == 1:
            # return flags
            return Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags


# TODO: instead of subclassing a delegate, try to find a way to supply a custom
#  itemEditorFactory function to the default QStyledItemDelegate
#  but this may not take care of setting model- and editor-data...
class Delegate(QStyledItemDelegate):
    # TODO: implement...
    def createEditor(self, parent, option, index, /) -> QWidget:
        return QComboBox(parent)

    # TODO: implement...
    def setEditorData(self, editor: QComboBox, index, /):
        editor.insertItems(0, ["1", "2", index.internalPointer().value])

    # TODO: implement...
    def setModelData(self, editor, model, index, /):
        pass


def main() -> None:
    settings_data = {
        "theme/style": "windows11",
        "theme/colorScheme": Qt.ColorScheme.Light,
        "windowState": 5,
        "windowGeometry": 1.6,
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
