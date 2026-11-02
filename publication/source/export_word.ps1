param([string[]]$Files = @('publication/Revised_Manuscript.docx','publication/Supporting_Reports.docx'))
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    foreach ($file in $Files) {
        $full = (Resolve-Path -LiteralPath $file).Path
        $pdf = [System.IO.Path]::ChangeExtension($full,'.pdf')
        $doc = $word.Documents.Open($full,$false,$true)
        try {
            $doc.Repaginate()
            $doc.ExportAsFixedFormat($pdf,17)
            Write-Output "Exported $pdf"
        } finally { $doc.Close(0) }
    }
} finally { $word.Quit() }
