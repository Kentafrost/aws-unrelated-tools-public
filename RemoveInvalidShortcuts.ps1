# 無効なショートカットを削除するPowerShellスクリプト

$directory = "D:*"  # 対象のディレクトリを指定
$shortcuts = Get-ChildItem -Path $directory -Filter *.lnk

foreach ($shortcut in $shortcuts) {
    $wshShell = New-Object -ComObject WScript.Shell
    $shortcutPath = $wshShell.CreateShortcut($shortcut.FullName).TargetPath
    if (-Not (Test-Path $shortcutPath)) {
        Write-Output "Deleting invalid shortcut: $($shortcut.FullName)"
        Remove-Item $shortcut.FullName
    }
}