from PySide6.QtCore import Qt, QAbstractItemModel


class TracesModel(QAbstractItemModel):
    def __init__(self, *args, traces=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.traces = traces or []

    def data(self, index, /, role = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            text = self.traces[index.row()]
            return text
        return None

    def rowCount(self, /, parent= ...):
        return len(self.traces)

    def update_traces(self, traces):
        self.traces = traces
        self.layoutChanged.emit()
