import sys
from functools import partial
from pathlib import Path
from typing import List

import pandas as pd

from end4train.app.device_connectors import OnLineListener, DataSource, LogDownloader
from end4train.app.settings import Settings
from end4train.communication.decode import decode_log_file, parse_p_packet, pivot_per_variable
from end4train.communication.ksy import KSYInfoStore
from end4train.config.paths import SETTINGS_JSON_FILE, RECORD_OBJECT_KSY_PATH
from end4train.ui.app import Gui


# TODO: rework using AnyIO
# TODO: design a way to call teardown for TimsDevice.stop()
# TODO: add device discovery (see. scratch.txt and handwritten notes)

# TODO: add map

# TODO: remove table

# TODO: use pglive

# TODO: add analog gauges (possibly implement a simple one from scratch...)

# TODO: add UI for selecting style and possibly overriding color theme

class Monitor:
    def __init__(self, argv: List[str]):
        self.data = pd.DataFrame()

        self.settings = Settings.model_validate_json(SETTINGS_JSON_FILE.read_text(), by_name=True)
        self.gui_app = Gui(
            argv, self.shutdown, self.data, self.toggle_listener, self.download_log, self.load_file, self.settings,
            self.save_settings
        )

        self.ksy_info_store = KSYInfoStore(RECORD_OBJECT_KSY_PATH)
        self.listener = OnLineListener(partial(self.add_data, source=DataSource.P_PACKET))
        self.downloader = LogDownloader(self.add_data, "hot")

    def save_settings(self, settings: Settings):
        self.settings = settings
        SETTINGS_JSON_FILE.write_text(settings.model_dump_json(indent=4))

    def shutdown(self):
        self.listener.stop("hot")
        self.listener.stop("eot")
        self.downloader.stop()

    def download_log(self, host: str):
        self.downloader = LogDownloader(self.add_data, host)
        self.downloader.download()

    def add_data(self, data, source: DataSource):
        if source == DataSource.LOG_FILE:
            loaded_data = decode_log_file(data, self.ksy_info_store.get_class_to_kaitai_type_map())
        elif source == DataSource.P_PACKET:
            loaded_data = parse_p_packet(data, self.ksy_info_store.get_class_to_kaitai_type_map())
        else:
            return
        # dataframe = merge_type_specific_dataframes(list(loaded_data.values()))
        # dataframe = pivot_per_variable(dataframe)
        dataframes = [pivot_per_variable(dataframe) for dataframe in loaded_data.values()]
        dataframe = pd.concat(dataframes, axis="columns")
        self.data = pd.concat([self.data, dataframe])
        # TODO: if possible, don't sort repeatedly
        self.data = self.data.sort_index()
        self.gui_app.add_data(dataframe)

    def toggle_listener(self, host: str, listen: bool):
        if listen:
            self.listener.listen(host)
        else:
            self.listener.stop(host)

    def load_file(self, file: Path):
        with open(file, "rb") as f:
            data = f.read()
        self.add_data(data, DataSource.LOG_FILE)

    def run(self):
        self.gui_app.exec()


def main() -> None:
    monitor_app = Monitor(sys.argv)
    sys.exit(monitor_app.run())


if __name__ == "__main__":
    main()
