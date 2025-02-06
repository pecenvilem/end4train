$ErrorActionPreference = "Stop"

$KSY_SPECS_DIR = ".\src\end4train\config\kaitai_specs"
$COMPILER_FOLDER = ".\kaitai-struct-compiler-0.11\bin\"
$COMPILER_OUTPUT_DIR = ".\src\end4train\communication\parsers\"
$PYTHON_PACKAGE = "end4train.communication.parsers"

Write-Output "============== KAITAI-STRUCT COMPILER INVOCATION =============="
Write-Output "Compiling files from: $KSY_SPECS_DIR"
Write-Output "Using compiler from $COMPILER_FOLDER"
Write-Output "Target folder: $COMPILER_OUTPUT_DIR"
Write-Output "Insering Python package import: $PYTHON_PACKAGE"

$files=Get-ChildItem $KSY_SPECS_DIR

$files | ForEach-Object {
    if ($_.FullName -match '.ksy$')
    {
        $cmd = "$COMPILER_FOLDER\kaitai-struct-compiler -t python -d $COMPILER_OUTPUT_DIR --python-package $PYTHON_PACKAGE -w $KSY_SPECS_DIR\$_"
        Invoke-Expression  $cmd
        Write-Output "Compiled file: $_"
    }
}
Write-Output "Finished sucesfully"
