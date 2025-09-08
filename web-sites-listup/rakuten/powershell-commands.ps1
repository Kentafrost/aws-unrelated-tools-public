# Add this to your PowerShell profile ($PROFILE)
function Invoke-RakutenFetcher {
    [CmdletBinding()]
    param()
    
    Write-Host "🛍️ Starting Rakuten Product Fetcher..." -ForegroundColor Green
    
    $scriptPath = "g:\My Drive\IT_Learning\Git\aws-unrelated-tools-private\web-sites-listup\rakuten\rakuten_item_listup_builtin.js"
    $workingDir = Split-Path $scriptPath -Parent
    
    if (Test-Path $scriptPath) {
        Push-Location $workingDir
        try {
            node $scriptPath
            Write-Host "✅ Rakuten products fetched successfully!" -ForegroundColor Green
            
            # Open results if available
            $csvPath = Join-Path $workingDir "results\rakuten_products.csv"
            if (Test-Path $csvPath) {
                Write-Host "📊 Opening results..." -ForegroundColor Yellow
                code $csvPath
            }
        }
        catch {
            Write-Error "❌ Failed to run script: $_"
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Error "❌ Script not found at: $scriptPath"
    }
}

# Alias for shorter command
Set-Alias rakuten Invoke-RakutenFetcher
