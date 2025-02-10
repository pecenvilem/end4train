from end4train.config.app import APP_NAME
from end4train.config.paths import LOGS_FOLDER

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {""
                     "format": "%(levelname)s\t%(asctime)s (%(name)s): %(message)s"}
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "D",
            "formatter": "standard",
            "filename": LOGS_FOLDER / f"{APP_NAME}.log"
        },
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "loggers": {
        "__main__": {"level": "DEBUG", "handlers": ["file", "console"]},
        "end4train.communication.mock_device.device": {"level": "DEBUG", "handlers": ["file", "console"]},
    },
}