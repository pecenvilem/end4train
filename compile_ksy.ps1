$files=Get-ChildItem .\kaitai\specs

$files | ForEach-Object {
    if ($_.FullName -match '.ksy$')
    {
        .\kaitai\kaitai-struct-compiler-0.11\bin\kaitai-struct-compiler -t python -d .\src\end4train\parsers\ --python-package end4train.parsers -w $_.FullName
    }
}