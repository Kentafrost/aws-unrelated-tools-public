# NPM EBADF Error Fix Script (PowerShell版)

Write-Host "=================================" -ForegroundColor Green
Write-Host "NPM EBADF Error Fix Script" -ForegroundColor Green  
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Step 1: npmキャッシュのクリア
Write-Host "Step 1: Cleaning npm cache..." -ForegroundColor Yellow
try {
    npm cache clean --force
    Write-Host "✓ npm cache cleaned successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Cache cleaning failed, continuing..." -ForegroundColor Orange
}

Write-Host ""

# Step 2: node_modulesの削除
Write-Host "Step 2: Removing node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "✓ node_modules removed" -ForegroundColor Green
} else {
    Write-Host "ℹ node_modules directory not found" -ForegroundColor Blue
}

Write-Host ""

# Step 3: package-lock.jsonの削除
Write-Host "Step 3: Removing package-lock.json..." -ForegroundColor Yellow
if (Test-Path "package-lock.json") {
    Remove-Item "package-lock.json"
    Write-Host "✓ package-lock.json removed" -ForegroundColor Green
} else {
    Write-Host "ℹ package-lock.json not found" -ForegroundColor Blue
}

Write-Host ""

# Step 4: 代替方法でのインストール
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow

$methods = @(
    @{Name="Standard install"; Command="npm install --verbose --no-optional"},
    @{Name="Legacy peer deps"; Command="npm install --legacy-peer-deps"},
    @{Name="Force install"; Command="npm install --force"},
    @{Name="Specific fluent-ffmpeg"; Command="npm install fluent-ffmpeg --no-optional --verbose"}
)

$success = $false

foreach ($method in $methods) {
    if ($success) { break }
    
    Write-Host "Trying: $($method.Name)..." -ForegroundColor Cyan
    
    try {
        Invoke-Expression $method.Command
        $success = $true
        Write-Host "✓ Success with: $($method.Name)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($method.Name)" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "Installation process completed" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# インストール状況の確認
Write-Host "Checking fluent-ffmpeg installation..." -ForegroundColor Yellow
try {
    npm list fluent-ffmpeg
    Write-Host "✓ fluent-ffmpeg check completed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not verify fluent-ffmpeg installation" -ForegroundColor Orange
}

Write-Host ""
Write-Host "If problems persist, try running PowerShell as Administrator" -ForegroundColor Yellow
Read-Host "Press Enter to continue"