from enum import StrEnum, auto

# noinspection SpellCheckingInspection
COMPANY = "fdcvut"
APP_NAME = "tims_monitor"

WINDOW_STATE_KEY = "windowState"
WINDOW_GEOMETRY_KEY = "windowGeometry"

class SaveOwner(StrEnum):
    SHUTDOWN_AUTOSAVE = "shutdownAutosave"
    USER = "user"

SETTINGS_VERSION_NUMBER = 0
