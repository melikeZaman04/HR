$ErrorActionPreference = "Stop"

Write-Host "Starting containers..."
docker compose up --build -d

Write-Host "Waiting for db to be healthy..."
do {
    Start-Sleep -Seconds 2
    $status = docker inspect -f "{{.State.Health.Status}}" ai_decision_db 2>$null
} while ($status -ne "healthy")

Write-Host "Running migrations..."
docker compose exec app alembic upgrade head

Write-Host "API docs: http://localhost:8000/docs"
