# Update an extracted ZIP checkout without replacing .venv or .cache.
param([Parameter(Mandatory=$true)][string]$ReleaseRef)
$ErrorActionPreference = "Stop"
if ($ReleaseRef -notmatch '^[0-9a-f]{40}$') { throw "Supply the full published commit SHA." }
if (!(Test-Path "pyproject.toml") -or
    !(Select-String -Path "pyproject.toml" -Pattern '^name = "semantic-search-benchmarker"$' -Quiet)) {
    throw "Run this from your AD331-semantic-search-benchmarker project folder."
}
$projectDirectory = (Get-Location).Path
$stageDirectory = Join-Path $env:TEMP ("semantic-memory-" + [guid]::NewGuid().ToString("N"))
$backupDirectory = Join-Path $stageDirectory "backup"
$files = @(
    "Dockerfile", "docker-compose.yml", "README.md", "ai_prompt_log.md",
    "src/indexer.py", "src/workbench.py", "src/vector_cache.py", "src/memory_probe.py",
    "tests/test_vector_cache.py", "docs/dell-verification.md",
    "docs/memory-optimization.md", "docs/memory-cached-profile.json", "docs/memory-qa.txt"
)
# Download every file successfully before changing the local project.
foreach ($file in $files) {
    $destination = Join-Path $stageDirectory $file
    New-Item -ItemType Directory -Force -Path (Split-Path $destination) | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/JohnNelson858/AD331-semantic-search-benchmarker/$ReleaseRef/$file" -OutFile $destination
}
foreach ($file in $files) {
    $destination = Join-Path $projectDirectory $file
    if (Test-Path $destination) {
        $backup = Join-Path $backupDirectory $file
        New-Item -ItemType Directory -Force -Path (Split-Path $backup) | Out-Null
        Copy-Item -LiteralPath $destination -Destination $backup
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $destination) | Out-Null
    Copy-Item -LiteralPath (Join-Path $stageDirectory $file) -Destination $destination -Force
}
Write-Host "Updated memory optimization files. Existing .venv and .cache preserved."
Write-Host "Previous files saved at: $backupDirectory"
Write-Host "Next: docker compose up --build -d --wait"
