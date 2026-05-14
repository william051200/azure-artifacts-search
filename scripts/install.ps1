<#
.SYNOPSIS
    Install or upgrade ArtifactLens on Windows (per-user, no admin required).

.DESCRIPTION
    Downloads the ArtifactLens.zip asset from a GitHub release, extracts it
    to a per-user folder, and creates Start Menu and Desktop shortcuts.

    Run via the standard one-liner:

        irm https://raw.githubusercontent.com/william051200/ArtifactLens/main/scripts/install.ps1 | iex

    Re-running the command upgrades an existing install in-place.

.PARAMETER InstallDir
    Override the install directory. Defaults to
    %LOCALAPPDATA%\Programs\ArtifactLens.

.PARAMETER Version
    Pin to a specific release tag (e.g. v1.0.0) instead of pulling the latest.

.PARAMETER NoShortcuts
    Skip Start Menu and Desktop shortcut creation.

.PARAMETER RestartApp
    Launch ArtifactLens.exe after the install completes (used by the in-app
    one-click upgrade flow).
#>

[CmdletBinding()]
param(
    [string]$InstallDir,
    [string]$Version,
    [switch]$NoShortcuts,
    [switch]$RestartApp
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo      = 'william051200/ArtifactLens'
$AssetName = 'ArtifactLens.zip'
$AppName   = 'ArtifactLens'
$ExeName   = 'ArtifactLens.exe'

if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
}

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

function Get-ReleaseInfo {
    if ($Version) {
        $url = "https://api.github.com/repos/$Repo/releases/tags/$Version"
    } else {
        $url = "https://api.github.com/repos/$Repo/releases/latest"
    }
    Write-Step "Fetching release info from $url"
    return Invoke-RestMethod -Uri $url -Headers @{ 'User-Agent' = 'ArtifactLens-Installer' }
}

function Get-AssetUrl($release) {
    $asset = $release.assets | Where-Object { $_.name -eq $AssetName } | Select-Object -First 1
    if (-not $asset) {
        throw "Release '$($release.tag_name)' does not contain an asset named '$AssetName'."
    }
    return $asset.browser_download_url
}

function Stop-RunningApp {
    Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($ExeName)) -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Step "Stopping running $ExeName (PID $($_.Id))..."
            Stop-Process -Id $_.Id -Force
        }
    Start-Sleep -Milliseconds 500
}

function Expand-Release($zipPath, $destDir) {
    $staging = Join-Path ([IO.Path]::GetTempPath()) ("ArtifactLens-stage-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $staging | Out-Null
    Expand-Archive -Path $zipPath -DestinationPath $staging -Force

    # Handle both flat-zip and top-level-folder layouts.
    $entries = Get-ChildItem -Path $staging
    $payloadRoot = $staging
    if ($entries.Count -eq 1 -and $entries[0].PSIsContainer) {
        $payloadRoot = $entries[0].FullName
    }

    if (Test-Path $destDir) {
        Write-Step "Removing previous install at $destDir"
        Remove-Item -Path $destDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    Copy-Item -Path (Join-Path $payloadRoot '*') -Destination $destDir -Recurse -Force
    Remove-Item -Path $staging -Recurse -Force -ErrorAction SilentlyContinue
}

function New-Shortcut($lnkPath, $targetExe) {
    $shell = New-Object -ComObject WScript.Shell
    $sc = $shell.CreateShortcut($lnkPath)
    $sc.TargetPath       = $targetExe
    $sc.WorkingDirectory = Split-Path $targetExe
    $sc.IconLocation     = "$targetExe,0"
    $sc.Save()
}

function New-Shortcuts($exePath) {
    $startMenuDir = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
    $startLink    = Join-Path $startMenuDir "$AppName.lnk"
    $desktopLink  = Join-Path ([Environment]::GetFolderPath('Desktop')) "$AppName.lnk"
    Write-Step "Creating Start Menu shortcut: $startLink"
    New-Shortcut -lnkPath $startLink -targetExe $exePath
    Write-Step "Creating Desktop shortcut:    $desktopLink"
    New-Shortcut -lnkPath $desktopLink -targetExe $exePath
}

try {
    $release = Get-ReleaseInfo
    $assetUrl = Get-AssetUrl $release
    Write-Step "Installing $AppName $($release.tag_name)"

    $tmpZip = Join-Path ([IO.Path]::GetTempPath()) "ArtifactLens-$($release.tag_name).zip"
    Write-Step "Downloading $assetUrl"
    Invoke-WebRequest -Uri $assetUrl -OutFile $tmpZip -UseBasicParsing
    Unblock-File -Path $tmpZip

    Stop-RunningApp
    Expand-Release -zipPath $tmpZip -destDir $InstallDir
    Remove-Item -Path $tmpZip -Force -ErrorAction SilentlyContinue

    $exePath = Join-Path $InstallDir $ExeName
    if (-not (Test-Path $exePath)) {
        throw "Installation finished but $ExeName was not found at $exePath."
    }

    if (-not $NoShortcuts) {
        New-Shortcuts -exePath $exePath
    }

    Write-Host ""
    Write-Host "$AppName $($release.tag_name) installed to $InstallDir" -ForegroundColor Green
    Write-Host "Launch it with: $exePath" -ForegroundColor Green

    if ($RestartApp) {
        Write-Step "Launching $ExeName"
        Start-Process -FilePath $exePath
    }
}
catch {
    Write-Host ""
    Write-Host "Install failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
