from typing import List, Literal, NamedTuple

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QFileDialog
import folium
from pandas.core.dtypes.common import is_numeric_dtype
from haversine import haversine_vector, Unit

from end4train.communication import OnLineListener, LogDownloader
from end4train.binary_parser import DataSource, get_data_from_process_data
from end4train.binary_parser import get_records_from_log_file, get_process_data_from_p_packet, get_process_data_from_records
from end4train.traces_model import TracesModel
from end4train.main_window import MainWindow
from end4train.dataframe_model import PandasModel


GPS_COLUMNS = ["eot_north", "eot_east", "hot_north", "hot_east"]
DEFAULT_GPS = (50.0833989, 14.4166467)


def has_both_device_coordinates(data: pd.DataFrame) -> bool:
    return all([column in data.columns for column in GPS_COLUMNS])


def get_coordinates(data: pd.DataFrame, device: Literal["eot", "hot"]) -> list[NamedTuple]:
    if device == "eot":
        return list(data[["eot_north", "eot_east"]].itertuples(index=False))
    return list(data[["hot_north", "hot_east"]].itertuples(index=False))


def calculate_device_distance(data: pd.DataFrame) -> pd.Series:
    if not has_both_device_coordinates(data):
        return pd.Series(np.nan, index=data.index)
    data = data[GPS_COLUMNS].replace(0, np.nan)
    eot_position = get_coordinates(data, "eot")
    hot_position = get_coordinates(data, "hot")
    return haversine_vector(eot_position, hot_position, unit=Unit.METERS, check=False)


class Monitor:
    def __init__(self, argv: List[str]):
        self._app = QApplication(argv)

        self.data = pd.DataFrame()
        self.data_model = PandasModel(self.data)

        self.traces_model = TracesModel()
        self.plot_traces = {}

        self.listener = OnLineListener(self.add_data)
        self.downloader = LogDownloader(self.add_data, "hot")

        self._app.aboutToQuit.connect(self.shutdown)

        self.main_window = MainWindow(
            self.toggle_listener, self.download_log, self.select_traces, self.traces_model, self.data_model,
        )

        self.plot = self.main_window.chart_view
        self.main_window.open_btn.clicked.connect(self.load_file)

        self.main_window.show()

    def shutdown(self):
        self.listener.stop("hot")
        self.listener.stop("eot")
        self.downloader.stop()

    def download_log(self, host: str):
        self.downloader = LogDownloader(self.add_data, host)
        self.downloader.download()

    def add_data(self, data, source: DataSource):
        if source == DataSource.LOG_FILE:
            records = get_records_from_log_file(data)
            process_data = get_process_data_from_records(records)
        elif source == DataSource.P_PACKET:
            process_data = get_process_data_from_p_packet(data)
        else:
            return
        dataframe = get_data_from_process_data(process_data)

        # # # TODO: testing - remove
        # if not has_both_device_coordinates(dataframe):
        #     dataframe["hot_north"] = np.random.uniform(49.6167797, 49.6220208, len(dataframe))
        #     dataframe["hot_east"] = np.random.uniform(15.5042428, 15.4904025, len(dataframe))
        #     dataframe["eot_north"] = np.random.uniform(49.6167797, 49.6220208, len(dataframe))
        #     dataframe["eot_east"] = np.random.uniform(15.5042428, 15.4904025, len(dataframe))
        #     pass
        # # # TODO: testing - remove

        dataframe["distance"] = calculate_device_distance(dataframe)
        self.data = pd.concat([self.data, dataframe])
        self.data = self.data.sort_index()
        selected_traces = self.main_window.get_selected_traces()
        self.data_model.set_new_data(self.data[selected_traces])
        self.traces_model.update_traces(self.data.columns.tolist())
        self.update_plot(list(self.plot_traces.keys()))

    def toggle_listener(self, host: str, listen: bool):
        if listen:
            self.listener.listen(host)
        else:
            self.listener.stop(host)

    def select_traces(self, selection):
        self.data_model.set_new_data(self.data[selection])
        for trace in self.plot_traces.copy():
            if trace not in selection:
                self.delete_plot(trace)
        for trace in selection:
            if trace not in self.plot_traces:
                self.add_plot(trace)

    def add_plot(self, trace: str):
        if not is_numeric_dtype(self.data[trace]):
            return
        self.plot.nextRow()
        plot = self.plot.addPlot(axisItems={'bottom': pg.DateAxisItem()})
        try:
            reference_plot = next(iter(self.plot_traces.values()))["plot_area"]
        except StopIteration:
            pass
        else:
            plot.setXLink(reference_plot)
        plot.setLabel("left", text=trace)
        data = self.data[trace].dropna()
        line = plot.plot(data.index.astype('int64') // 10 ** 9, data.to_list())
        self.plot_traces[trace] = {
            "plot_area": plot,
            "data_line": line
        }

    def delete_plot(self, trace: str):
        plot_info = self.plot_traces.pop(trace)
        self.plot.removeItem(plot_info["plot_area"])

    def update_plot(self, traces: List[str]):
        for trace in traces:
            data = self.data[trace].dropna()
            self.plot_traces[trace]["data_line"].setData(data.index.astype('int64') // 10 ** 9, data.to_list())

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(parent=self.main_window)
        with open(path, "rb") as f:
            data = f.read()
        self.add_data(data, DataSource.LOG_FILE)

    def run(self):
        self._app.exec()