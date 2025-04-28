from __future__ import annotations

import os
import platformdirs
from pathlib import Path

from dotenv import load_dotenv

from end4train.config.app import APP_NAME, COMPANY
from end4train.config.env_variables import EnvVariable

load_dotenv()

PATHS_FILE = Path(__file__)
CONFIG_FOLDER = PATHS_FILE.parent
PACKAGE_FOLDER = CONFIG_FOLDER.parent
UI_FOLDER = PACKAGE_FOLDER / "ui"
UI_RESOURCES_FOLDER = UI_FOLDER / "res"
KAITAI_SPEC_FOLDER = CONFIG_FOLDER / "kaitai_specs"
RECORD_OBJECT_KSY_PATH = KAITAI_SPEC_FOLDER / "record_object.ksy"
LOGS_FOLDER = Path(
    os.environ.get(
        EnvVariable.LOG_FILE_DIR,
        platformdirs.user_log_dir(APP_NAME, COMPANY)
    )
)
SETTINGS_JSON_FILE = CONFIG_FOLDER / "settings.json"
SAMPLE_DATA_PARQUET_FOLDER = Path(__file__).parent / "sample_data"
HOT_SAMPLE_PARQUET_FOLDER = SAMPLE_DATA_PARQUET_FOLDER / "hot"
EOT_SAMPLE_PARQUET_FOLDER = SAMPLE_DATA_PARQUET_FOLDER / "eot"

NEEDLE_SVG_FILE = UI_RESOURCES_FOLDER / "needle.svg"
OBE_BASE_SVG_FILE = UI_RESOURCES_FOLDER / "obe_base.svg"
OBE_RING_SVG_FILE = UI_RESOURCES_FOLDER / "obe_ring.svg"
