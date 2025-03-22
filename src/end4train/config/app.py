from enum import StrEnum, auto

# noinspection SpellCheckingInspection
COMPANY = "fdcvut"
APP_NAME = "tims_monitor"


class SettingsKey(StrEnum):
    WINDOW_STATE = "windowState"
    GEOMETRY_STATE = "windowGeometry"
    STYLE = "theme/style"
    COLOR_SCHEME = "theme/colorScheme"


class SaveOwner(StrEnum):
    SHUTDOWN_AUTOSAVE = "shutdownAutosave"
    USER = "user"

SETTINGS_VERSION_NUMBER = 0
