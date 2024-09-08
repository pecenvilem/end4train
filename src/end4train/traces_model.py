from PySide6.QtCore import QAbstractListModel, Qt


class TracesModel(QAbstractListModel):
    def __init__(self, *args, traces=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.traces = traces or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.traces[index.row()]
            return text

    def rowCount(self, index):
        return len(self.traces)

    def update_traces(self, traces):
        self.traces = traces
        self.layoutChanged.emit()
