# NVDA Add-on build script (clean & safe)

$addonName = "ModifiedWordSpeech"

# legge versione dal manifest
$version = (Select-String -Path "manifest.ini" -Pattern "^version").Line.Split("=")[1].Trim()

# path base
$root = Get-Location

$buildRoot = "C:\Dev\NVDA\build"
$buildDir = Join-Path $buildRoot "$addonName-$version"

$distDir = Join-Path $root "dist"
$addonFile = Join-Path $distDir "$addonName-$version.nvda-addon"

Write-Host "Building NVDA addon version $version..."

# crea cartelle se mancanti
if (!(Test-Path $buildRoot)) {
    New-Item -ItemType Directory -Path $buildRoot | Out-Null
}

if (!(Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

# pulizia build precedente
if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
}

New-Item -ItemType Directory -Path $buildDir | Out-Null

# =========================
# COPIA SOLO FILE NECESSARI
# =========================

Copy-Item -Recurse -Force "$root\globalPlugins" $buildDir
Copy-Item -Recurse -Force "$root\locale" $buildDir
Copy-Item -Force "$root\manifest.ini" $buildDir

# =========================
# CREA ADDON (.nvda-addon)
# =========================

if (Test-Path $addonFile) {
    Remove-Item $addonFile -Force
}

Compress-Archive -Path "$buildDir\*" -DestinationPath $addonFile

# =========================
# VERIFICA FINALE
# =========================

if (Test-Path $addonFile) {
    Write-Host "DONE -> $addonFile"
} else {
    Write-Host "ERROR: build failed"
}