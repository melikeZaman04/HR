$ErrorActionPreference = "Stop"

$resultsDir = Join-Path $PSScriptRoot "results"
if (-not (Test-Path $resultsDir)) {
    throw "results klasoru bulunamadi: $resultsDir"
}

$runFiles = Get-ChildItem $resultsDir -File -Filter "demo_run_*.json" | Sort-Object LastWriteTime
if (-not $runFiles) {
    throw "Rapor olusturmak icin demo_run_*.json bulunamadi."
}

$allRuns = @()
foreach ($file in $runFiles) {
    $raw = Get-Content $file.FullName -Raw
    $obj = $raw | ConvertFrom-Json

    $ceo = $obj.simulation_response.agent_outputs | Where-Object { $_.agent_name -eq "CEO" } | Select-Object -First 1
    $cfo = $obj.simulation_response.agent_outputs | Where-Object { $_.agent_name -eq "CFO" } | Select-Object -First 1
    $hr  = $obj.simulation_response.agent_outputs | Where-Object { $_.agent_name -eq "HR" } | Select-Object -First 1

    $allRuns += [PSCustomObject]@{
        file_name = $file.Name
        timestamp = $obj.timestamp
        scenario_id = $obj.create_response.scenario_id
        final_score = $obj.simulation_response.final_score
        final_decision = $obj.simulation_response.final_decision
        ceo_score = if ($ceo) { $ceo.score } else { $null }
        cfo_score = if ($cfo) { $cfo.score } else { $null }
        hr_score = if ($hr) { $hr.score } else { $null }
        ceo_rationale = if ($ceo) { $ceo.rationale } else { "" }
        cfo_rationale = if ($cfo) { $cfo.rationale } else { "" }
        hr_rationale = if ($hr) { $hr.rationale } else { "" }
    }
}

$latest = $allRuns | Sort-Object timestamp | Select-Object -Last 1
$approved = @($allRuns | Where-Object { $_.final_decision -eq "APPROVE" }).Count
$revised = @($allRuns | Where-Object { $_.final_decision -eq "REVISE" }).Count
$rejected = @($allRuns | Where-Object { $_.final_decision -eq "REJECT" }).Count

$summary = [PSCustomObject]@{
    generated_at = (Get-Date).ToString("o")
    total_runs = $allRuns.Count
    decisions = [PSCustomObject]@{
        APPROVE = $approved
        REVISE = $revised
        REJECT = $rejected
    }
    latest = $latest
}

$bundle = [PSCustomObject]@{
    summary = $summary
    runs = $allRuns
}

$bundlePath = Join-Path $resultsDir "all_demo_runs.json"
$archivePath = Join-Path $resultsDir ("all_demo_runs_snapshot_{0}.json" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

$bundleJson = $bundle | ConvertTo-Json -Depth 20
$bundleJson | Set-Content -Path $bundlePath -Encoding utf8
$bundleJson | Set-Content -Path $archivePath -Encoding utf8

$htmlTemplate = @'
<!doctype html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Multiagent Demo Raporu</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f6f8fb; color: #1f2937; }
    .wrap { max-width: 1100px; margin: 0 auto; }
    .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 10px; }
    .kpi { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }
    .kpi .label { font-size: 12px; color: #6b7280; }
    .kpi .value { font-size: 24px; font-weight: 700; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #e5e7eb; text-align: left; padding: 8px; vertical-align: top; }
    th { background: #f3f4f6; }
    .badge { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
    .APPROVE { background: #dcfce7; color: #166534; }
    .REVISE { background: #fef3c7; color: #92400e; }
    .REJECT { background: #fee2e2; color: #991b1b; }
    .small { font-size: 12px; color: #6b7280; }
    pre { white-space: pre-wrap; margin: 0; font-size: 12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>AI Decision Ecosystem Engine — Demo Sonuc Raporu</h1>
    <p class="small">Bu sayfa otomatik uretilmistir ve tum onceki JSON calisma sonuclarini listeler.</p>

    <div class="card" id="summary"></div>

    <div class="card">
      <h2>Calisma Gecmisi</h2>
      <table>
        <thead>
          <tr>
            <th>Dosya</th>
            <th>Timestamp</th>
            <th>Scenario ID</th>
            <th>CEO</th>
            <th>CFO</th>
            <th>HR</th>
            <th>Final Score</th>
            <th>Decision</th>
          </tr>
        </thead>
        <tbody id="runs"></tbody>
      </table>
    </div>

    <div class="card">
      <h2>Agent Rationales (Son Kosu)</h2>
      <div id="rationales"></div>
    </div>
  </div>

  <script>
    const data = __DATA__;

    function escapeHtml(value) {
      return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    const summary = data.summary;
    const runs = data.runs || [];

    document.getElementById('summary').innerHTML = `
      <h2>Ozet</h2>
      <div class="grid">
        <div class="kpi"><div class="label">Toplam Kosu</div><div class="value">${summary.total_runs}</div></div>
        <div class="kpi"><div class="label">APPROVE</div><div class="value">${summary.decisions.APPROVE}</div></div>
        <div class="kpi"><div class="label">REVISE</div><div class="value">${summary.decisions.REVISE}</div></div>
        <div class="kpi"><div class="label">REJECT</div><div class="value">${summary.decisions.REJECT}</div></div>
      </div>
      <p class="small">Generated: ${summary.generated_at}</p>
    `;

    const rowsHtml = runs.map(run => `
      <tr>
        <td>${escapeHtml(run.file_name)}</td>
        <td>${escapeHtml(run.timestamp)}</td>
        <td>${escapeHtml(run.scenario_id)}</td>
        <td>${escapeHtml(run.ceo_score)}</td>
        <td>${escapeHtml(run.cfo_score)}</td>
        <td>${escapeHtml(run.hr_score)}</td>
        <td>${escapeHtml(run.final_score)}</td>
        <td><span class="badge ${escapeHtml(run.final_decision)}">${escapeHtml(run.final_decision)}</span></td>
      </tr>
    `).join('');

    document.getElementById('runs').innerHTML = rowsHtml;

    const latest = summary.latest || {};
    document.getElementById('rationales').innerHTML = `
      <p><strong>Scenario ID:</strong> ${escapeHtml(latest.scenario_id)} | <strong>Decision:</strong> <span class="badge ${escapeHtml(latest.final_decision)}">${escapeHtml(latest.final_decision)}</span></p>
      <h3>CEO</h3><pre>${escapeHtml(latest.ceo_rationale)}</pre>
      <h3>CFO</h3><pre>${escapeHtml(latest.cfo_rationale)}</pre>
      <h3>HR</h3><pre>${escapeHtml(latest.hr_rationale)}</pre>
    `;
  </script>
</body>
</html>
'@

$embedded = $htmlTemplate.Replace("__DATA__", $bundleJson)
$htmlPath = Join-Path $resultsDir "report.html"
$embedded | Set-Content -Path $htmlPath -Encoding utf8

[PSCustomObject]@{
    total_runs = $allRuns.Count
    all_runs_file = $bundlePath
    snapshot_file = $archivePath
    report_file = $htmlPath
} | ConvertTo-Json -Depth 5
