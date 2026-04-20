Param(
    [string]$Name = "JSON Kayit Demo",
    [string]$Description = "Sonuclari JSON kaydet",
    [double]$BudgetMillionUsd = 2.0,
    [double]$ExpectedRoiPercent = 80,
    [int]$RiskLevel = 2,
    [int]$TeamReadiness = 8
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

function Invoke-DockerCommand {
    param(
        [string]$Command
    )

    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = (& cmd /c ("docker {0}" -f $Command)) 2>&1 | Out-String
    $success = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $previousErrorAction

    return @{
        success = $success
        output = $output.Trim()
    }
}

$resultsDir = Join-Path $PSScriptRoot "results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
}

$timestampFile = Get-Date -Format "yyyyMMdd_HHmmss"
$runFile = Join-Path $resultsDir ("demo_run_{0}.json" -f $timestampFile)
$latestFile = Join-Path $resultsDir "latest_demo_result.json"

$payload = @{
    name = $Name
    description = $Description
    budget_million_usd = $BudgetMillionUsd
    expected_roi_percent = $ExpectedRoiPercent
    risk_level = $RiskLevel
    team_readiness = $TeamReadiness
}

$composeUp = Invoke-DockerCommand -Command "compose up -d"
$migration = Invoke-DockerCommand -Command "compose exec -e PYTHONPATH=/app app alembic upgrade head"

$create = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/scenarios" -ContentType "application/json" -Body ($payload | ConvertTo-Json)
$id = $create.scenario_id
$simulate = Invoke-RestMethod -Method Post -Uri ("http://localhost:8000/api/v1/scenarios/{0}/simulate" -f $id)
$retrieve = Invoke-RestMethod -Method Get -Uri ("http://localhost:8000/api/v1/scenarios/{0}/simulation" -f $id)
$swagger = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing
$composePs = Invoke-DockerCommand -Command "compose ps"

$result = @{
    timestamp = (Get-Date).ToString("o")
    compose_up = $composeUp
    migration = $migration
    compose_ps = $composePs
    create_request = $payload
    create_response = $create
    simulation_response = $simulate
    retrieve_response = $retrieve
    swagger = @{
        status_code = $swagger.StatusCode
        status_description = $swagger.StatusDescription
    }
}

$json = $result | ConvertTo-Json -Depth 20
$json | Set-Content -Path $runFile -Encoding utf8
$json | Set-Content -Path $latestFile -Encoding utf8

[PSCustomObject]@{
    run_file = $runFile
    latest_file = $latestFile
    scenario_id = $id
    final_score = $simulate.final_score
    final_decision = $simulate.final_decision
} | ConvertTo-Json -Depth 5
