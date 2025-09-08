# install all libraries in requirements.txt
# PowerShellで実行するためのPythonパッケージインストールスクリプト

Write-Host "Installing Python packages from requirements.txt..." -ForegroundColor Green

# Get the current directory
$currentDir = Get-Location

# Check if requirements.txt exists
if (Test-Path "$currentDir\requirements.txt") {
    Write-Host "Found requirements.txt in: $currentDir" -ForegroundColor Yellow
    
    # Try different Python executables
    $pythonExes = @(
        "python",
        "python3",
        "py",
        "C:\Program Files\Python312\python.exe"
    )
    
    $pythonFound = $false
    
    foreach ($pythonExe in $pythonExes) {
        try {
            $version = & $pythonExe --version 2>$null
            if ($version) {
                Write-Host "Using Python: $pythonExe ($version)" -ForegroundColor Cyan
                
                # Install packages
                & $pythonExe -m pip install -r requirements.txt
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Successfully installed all packages!" -ForegroundColor Green
                } else {
                    Write-Host "Failed to install packages" -ForegroundColor Red
                }
                
                $pythonFound = $true
                break
            }
        }
        catch {
            continue
        }
    }
    
    if (-not $pythonFound) {
        Write-Host "Python not found. Please install Python or add it to PATH" -ForegroundColor Red
        exit 1
    }
    
} else {
    Write-Host "requirements.txt not found in current directory: $currentDir" -ForegroundColor Red
    exit 1
}