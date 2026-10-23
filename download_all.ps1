# Download the whole interior-models library (10 GitHub repos, ~6.5 GB) into a local folder, e.g. D:\interior-models
# Usage: powershell -ExecutionPolicy Bypass -File download_all.ps1 [-Dest D:\interior-models]
param([string]$Dest = "D:\interior-models")
$ErrorActionPreference = "Stop"
$repos = "interior-models","interior-models-ikea","interior-models-ikea-2","interior-models-ikea-3","interior-models-extra","interior-models-objaverse","interior-models-objaverse-2","interior-models-objaverse-3","interior-models-materials","interior-models-layouts"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
foreach ($r in $repos) {
  $zip = Join-Path $env:TEMP "$r.zip"
  $url = "https://github.com/iandamai720-cmyk/$r/archive/refs/heads/main.zip"
  Write-Host "Downloading $url"
  Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
  $out = Join-Path $Dest $r
  if (Test-Path $out) { Remove-Item -Recurse -Force $out }
  Expand-Archive -Path $zip -DestinationPath $Dest -Force
  Rename-Item (Join-Path $Dest "$r-main") $r
  Remove-Item $zip
}
Write-Host "Done -> $Dest  (catalog: $Dest\interior-models\catalog.json; file URLs map to $Dest\<repo>\<path>)"
