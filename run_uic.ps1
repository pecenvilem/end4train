$ErrorActionPreference = "Stop"

$UI_FILE_DIR = ".\qt_designer"
$OUTPUT_DIR = ".\src\end4train\ui"

Write-Output "============== UIC INVOCATION =============="
Write-Output "Compiling files from: $UI_FILE_DIR"
Write-Output "Target folder: $OUTPUT_DIR"

$files=Get-ChildItem $UI_FILE_DIR

$files | ForEach-Object {
    if ($_.FullName -match '.ui$')
    {
        $cmd = "pyside6-uic.exe -g python -o $OUTPUT_DIR\$($_.BaseName)_ui.py $UI_FILE_DIR\$_"
        Invoke-Expression  $cmd
        Write-Output "Compiled file: $_"
    }
}
Write-Output "Finished sucesfully"



#pyside6-uic.exe -g python -o src/end4train/ui/main_window_ui.py qt_designer/monitor_main_window.ui