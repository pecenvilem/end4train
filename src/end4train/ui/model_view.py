from __future__ import annotations
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable, Any
import faulthandler

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject
from PySide6.QtWidgets import QApplication, QTreeView
from nuitka.ModuleRegistry import root_modules


def drop_duplicates(original: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(original))

@dataclass
class SettingsNode:
    path: str = "/"
    parent: SettingsNode | None = None
    children: dict[str, SettingsNode] = field(default_factory=dict)
    value: Any = None

    def __post_init__(self) -> None:
        self.stem = self.path.split("/")[-1]


class SettingsModel(QAbstractItemModel):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._headers = ("key", "value")
        self.data_store = {
            "theme/style": "Style",
            "theme/colorScheme": "Scheme",
            "windowState": "State",
            "windowGeometry": "Geo",
        }
        self.root_node = SettingsModel.build_tree(self.data_store)

        # needed to keep ref_count for "implicit" keys e.g. 'theme' for 'theme/style',
        # because Qt doesn't keep it and interpreter would GC them
        self._key_ref = list()

    @staticmethod
    def build_tree(settings: dict) -> SettingsNode:
        root = SettingsNode()
        for key, value in settings.items():
            levels = SettingsModel.split_levels(key)
            parent = root
            path = ""
            for i, level in enumerate(levels):
                path = f"{path}/{level}"
                if path not in parent.children:
                    node = SettingsNode(path, parent, {}, value if i+1 == len(levels) else None)
                    parent.children[path] = node
                parent = parent.children[path]
        return root

    @staticmethod
    def split_levels(key: str) -> list[str]:
        return key.split("/")

    @staticmethod
    def get_rank(key: str) -> int:
        return len(SettingsModel.split_levels(key)) if key != "" else 0

    @staticmethod
    def levels_before_rank(key: str, rank: int) -> str:
        # TODO: add check for negative rank and define custom exception
        levels = SettingsModel.split_levels(key)
        return "/".join(levels[0:rank])

    @staticmethod
    def get_parent_key(key: str) -> str:
        levels = SettingsModel.split_levels(key)
        parent_levels = levels[:-1]
        if not parent_levels:
            return ""
        return "/".join(parent_levels)

    def get_descendants(self, key: str) -> list[str]:
        descendants = []
        for other_key in self.data_store:
            if other_key == key:
                continue
            if not other_key.startswith(key):
                continue
            descendants.append(other_key)
        return descendants

    def get_children(self, key: str) -> list[str]:
        descendants = self.get_descendants(key)
        rank = SettingsModel.get_rank(key)
        return drop_duplicates(
            SettingsModel.levels_before_rank(descendant, rank + 1) for descendant in descendants
        )

    def get_index_in_parent(self, key: str) -> int:
        # return self.get_children(key).index(key)
        parent_key = SettingsModel.get_parent_key(key)
        return self.get_children(parent_key).index(key)

    def get_child(self, parent: str, index: int) -> str:
        return self.get_children(parent)[index]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None


    def setData(self, index, value, /, role = ...):
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                key = index.internalPointer()
                self.data_store[key] = str(value)
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
        parent_key = parent.internalPointer() if parent.isValid() else ""
        child_key = self.get_child(parent_key, row)
        self._key_ref.append(child_key)
        return self.createIndex(row, column, child_key)

    @lru_cache
    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        child_key = index.internalPointer()
        parent_key = SettingsModel.get_parent_key(child_key)

        if parent_key == "":
            return QModelIndex()

        row = self.get_index_in_parent(index.internalPointer())
        self._key_ref.append(parent_key)
        return self.createIndex(row, 0, parent_key)

    @lru_cache
    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_key = ""
        else:
            parent_key = parent.internalPointer()
        children = self.get_children(parent_key)
        return len(children)

    @lru_cache
    def columnCount(self, parent: QModelIndex = ...):
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super().flags(index)

        if index.column() == 1:
            return flags
            # return Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags


def main() -> None:
    app = QApplication(sys.argv)
    tree_view = QTreeView()
    model = SettingsModel(app)
    tree_view.setModel(model)
    tree_view.show()
    app.exec()


if __name__ == "__main__":
    faulthandler.enable()
    main()
