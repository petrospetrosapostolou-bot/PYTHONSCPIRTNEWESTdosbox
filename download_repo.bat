@echo off
REM download_repo.bat
REM Downloads and extracts an entire GitHub repo (branch) into a local folder.
REM Usage: download_repo.bat [branch] [output_dir]
REM Example: download_repo.bat main C:\temp\repo

SETLOCAL ENABLEDELAYEDEXPANSION

:: Default repository (adjust if you want different defaults)
set "OWNER=petrospetrosapostolou-bot"
set "REPO=PYTHONSCPIRTNEWESTdosbox"
set "BRANCH=main"
set "SCRIPT_DIR=%~dp0"

if not "%~1"=="" set "BRANCH=%~1"
if not "%~2"=="" set "OUTDIR=%~2"

if "%OUTDIR%"=="" set "OUTDIR=%SCRIPT_DIR%%REPO%-%BRANCH%"

echo.
echo Downloading %OWNER%/%REPO% (branch: %BRANCH%) to "%OUTDIR%"
echo.

:: Try git clone if git is available (preserves full git history)
where git >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Git found — using git clone...
    if exist "%OUTDIR%" (
        echo Output directory exists. Use a different folder or remove "%OUTDIR%".
        goto :end
    )
    git clone --depth 1 --branch "%BRANCH%" "https://github.com/%OWNER%/%REPO%.git" "%OUTDIR%"
    if %ERRORLEVEL% == 0 (
        echo Clone complete.
        goto :end
    ) else (
        echo Git clone failed — falling back to ZIP download.
    )
)

:: Use PowerShell to download ZIP and extract (works on Windows with PowerShell)
set "ZIPFILE=%SCRIPT_DIR%%REPO%-%BRANCH%.zip"

powershell -NoProfile -Command ^
  "$url = 'https://github.com/%OWNER%/%REPO%/archive/refs/heads/%BRANCH%.zip';" ^
  "Write-Host 'Downloading' $url;" ^
  "try { Invoke-WebRequest -Uri $url -OutFile '%ZIPFILE%' -UseBasicParsing -ErrorAction Stop } catch { Write-Error 'Download failed.'; exit 2 };" ^
  "if (Test-Path '%ZIPFILE%') { " ^
    "if (-not (Test-Path '%OUTDIR%')) { New-Item -ItemType Directory -Path '%OUTDIR%' | Out-Null };" ^
    "try { Expand-Archive -LiteralPath '%ZIPFILE%' -DestinationPath '%OUTDIR%' -Force; } catch { Write-Error 'Extraction failed.'; Remove-Item '%ZIPFILE%' -Force -ErrorAction SilentlyContinue; exit 3 };" ^
    "Remove-Item '%ZIPFILE%' -Force -ErrorAction SilentlyContinue;" ^
    "Write-Host 'Downloaded and extracted to %OUTDIR%'; exit 0 } else { Write-Error 'ZIP file not found after download.'; exit 4 }"

if %ERRORLEVEL% == 0 (
    echo Done.
) else (
    echo There was a problem downloading or extracting the repository. Error code %ERRORLEVEL%.
)

:end
echo.
pause
