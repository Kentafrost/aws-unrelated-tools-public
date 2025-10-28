# check_npm.ps1 - npm環境確認スクリプト

Write-Host "=== npm Environment Check ===" -ForegroundColor Green
Write-Host ""

# Node.jsとnpmの確認
Write-Host "1. Checking Node.js and npm installation..." -ForegroundColor Yellow

# Node.jsの確認
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
}

# npmの確認（複数の方法）
Write-Host ""
Write-Host "2. Checking npm with different methods..." -ForegroundColor Yellow

# Method 1: Get-Command
try {
    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmCmd) {
        Write-Host "✅ npm found with Get-Command: $($npmCmd.Source)" -ForegroundColor Green
    } else {
        Write-Host "❌ npm not found with Get-Command" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error using Get-Command for npm" -ForegroundColor Red
}

# Method 2: where.exe (Windows where command)
try {
    $npmWhere = where.exe npm 2>$null
    if ($npmWhere) {
        Write-Host "✅ npm found with where.exe: $npmWhere" -ForegroundColor Green
    } else {
        Write-Host "❌ npm not found with where.exe" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error using where.exe for npm" -ForegroundColor Red
}

# Method 3: Direct npm version check
try {
    $npmVersion = npm --version 2>$null
    if ($npmVersion) {
        Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ npm version command failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error getting npm version" -ForegroundColor Red
}

# PATH環境変数の確認
Write-Host ""
Write-Host "3. Checking PATH environment variable..." -ForegroundColor Yellow
$pathDirs = $env:PATH -split ';'
$nodejsPaths = $pathDirs | Where-Object { $_ -like "*nodejs*" -or $_ -like "*npm*" }

if ($nodejsPaths) {
    Write-Host "✅ Node.js related paths found in PATH:" -ForegroundColor Green
    foreach ($path in $nodejsPaths) {
        Write-Host "   - $path" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ No Node.js related paths found in PATH" -ForegroundColor Red
}

# 一般的なNode.jsインストール場所の確認
Write-Host ""
Write-Host "4. Checking common Node.js installation locations..." -ForegroundColor Yellow

$commonPaths = @(
    "C:\Program Files\nodejs\npm.cmd",
    "C:\Program Files (x86)\nodejs\npm.cmd", 
    "$env:APPDATA\npm\npm.cmd",
    "$env:LOCALAPPDATA\Programs\nodejs\npm.cmd"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Found npm at: $path" -ForegroundColor Green
    }
}

# PowerShellプロファイルの確認
Write-Host ""
Write-Host "5. Checking PowerShell profile..." -ForegroundColor Yellow
if (Test-Path $PROFILE) {
    Write-Host "✅ PowerShell profile exists: $PROFILE" -ForegroundColor Green
    $profileContent = Get-Content $PROFILE -Raw
    if ($profileContent -like "*nodejs*" -or $profileContent -like "*npm*") {
        Write-Host "✅ Node.js/npm configuration found in profile" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️ PowerShell profile not found (this is normal)" -ForegroundColor Blue
}

Write-Host ""
Write-Host "=== Recommendations ===" -ForegroundColor Green

# 問題がある場合の推奨事項
try {
    $testNpm = npm --version 2>$null
    if (-not $testNpm) {
        Write-Host ""
        Write-Host "❌ npm is not working properly. Try these solutions:" -ForegroundColor Red
        Write-Host ""
        Write-Host "Solution 1: Restart PowerShell and try again" -ForegroundColor Yellow
        Write-Host "Solution 2: Add Node.js to PATH manually:" -ForegroundColor Yellow
        Write-Host '   $env:PATH += ";C:\Program Files\nodejs"' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Solution 3: Reinstall Node.js from https://nodejs.org" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Solution 4: Use full path to npm:" -ForegroundColor Yellow
        Write-Host '   & "C:\Program Files\nodejs\npm.cmd" install fluent-ffmpeg' -ForegroundColor Cyan
    } else {
        Write-Host "✅ npm is working correctly!" -ForegroundColor Green
        Write-Host "You can now run: npm install fluent-ffmpeg" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ npm test failed" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue"