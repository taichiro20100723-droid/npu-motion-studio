$ErrorActionPreference = 'SilentlyContinue'

# Stop only the local NPU Motion Studio listener.
$connections = Get-NetTCPConnection -LocalPort 7862 -State Listen
foreach ($connection in $connections) {
    Stop-Process -Id $connection.OwningProcess -Force
}
