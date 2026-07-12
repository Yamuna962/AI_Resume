# Start backend — frees port 8000 if already in use
$port = 8000

$listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique

foreach ($pid in $listeners) {
    if ($pid -gt 0) {
        Write-Host "Stopping process $pid on port $port..."
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 1

$stillBusy = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($stillBusy) {
    Write-Host "ERROR: Port $port is still in use. Close other terminals running uvicorn, then retry."
    exit 1
}

Write-Host "Applying Alembic migrations..."
python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Alembic migration failed. Fix the database/config issue and retry."
    exit $LASTEXITCODE
}

Write-Host "Starting backend on http://0.0.0.0:$port ..."
python -m uvicorn main:app --host 0.0.0.0 --port $port
