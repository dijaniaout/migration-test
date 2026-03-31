$baseDir = "c:\OdooProject\odoo-modules\collection_disputes_base"
$mgmtDir = "c:\OdooProject\odoo-modules\collection_disputes_management"

$files = Get-ChildItem -Path $mgmtDir -Recurse -Include *.py, *.xml, *.csv | Where-Object { $_.FullName -notmatch "__pycache__" }

foreach ($file in $files) {
    $relPath = $file.FullName.Substring($mgmtDir.Length + 1)
    $basePath = Join-Path $baseDir $relPath
    
    if (Test-Path $basePath) {
        $mgmtContent = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
        $baseContent = [System.IO.File]::ReadAllText($basePath, [System.Text.Encoding]::UTF8)
        
        $mgmtClean = $mgmtContent -replace "collection_disputes_management", "collection_disputes_base"
        
        if ($mgmtClean -eq $baseContent) {
            Write-Host "DELETING IDENTICAL: $relPath"
            Remove-Item $file.FullName -Force
        } else {
            Write-Host "MODIFIED: $relPath"
        }
    } else {
        Write-Host "NEW FILE: $relPath"
    }
}
