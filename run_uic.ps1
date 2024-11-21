$VIRTUAL_ENV = poetry env info --path
$UIC_CALL = "$VIRTUAL_ENV\Lib\site-packages\PySide6\uic.exe -g python -o src/end4train/ui/main_window_ui.py qt_designer/monitor_main_window.ui"
Invoke-Expression $UIC_CALL
