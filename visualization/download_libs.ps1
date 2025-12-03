# Download JavaScript libraries for offline use
$libs = @{
    "socket.io.min.js" = "https://cdn.socket.io/4.5.4/socket.io.min.js"
    "vis-network.min.js" = "https://unpkg.com/vis-network@latest/standalone/umd/vis-network.min.js"
    "chart.umd.min.js" = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
}

foreach ($file in $libs.Keys) {
    $url = $libs[$file]
    $output = "visualization\static\libs\$file"
    Write-Host "Downloading $file..."
    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host "  ✅ Downloaded $file"
    } catch {
        Write-Host "  ❌ Failed to download $file"
    }
}

Write-Host "`nDone! Libraries saved to visualization\static\libs\"

