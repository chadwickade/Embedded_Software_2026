[CmdletBinding()]
param(
    [ValidateSet("pdf", "clean")]
    [string]$Action = "pdf",
    [switch]$InstallMissingPackages
)

$ErrorActionPreference = "Stop"
$Main = "embswManual"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallerOption = if ($InstallMissingPackages) { '--enable-installer' } else { '--disable-installer' }

# Use the standard existing per-user MiKTeX install when it is not on PATH.
# This changes only the current build process, not the user's system settings.
if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
    $MiKTeXBin = Join-Path $env:LOCALAPPDATA 'Programs\MiKTeX\miktex\bin\x64'
    if (Test-Path -LiteralPath (Join-Path $MiKTeXBin 'pdflatex.exe')) {
        $env:PATH = $MiKTeXBin + ';' + $env:PATH
    }
}
if (-not (Get-Command perl -ErrorAction SilentlyContinue)) {
    foreach ($PerlBin in @('C:\msys64\usr\bin', (Join-Path $env:ProgramFiles 'Git\usr\bin'))) {
        if (Test-Path -LiteralPath (Join-Path $PerlBin 'perl.exe')) {
            $env:PATH = $PerlBin + ';' + $env:PATH
            break
        }
    }
}

function Assert-Tool {
    param([string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required tool '$Name' was not found on PATH."
    }
}

function Invoke-Tool {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    & $Name @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

Push-Location $Root
try {
    switch ($Action) {
        "pdf" {
            foreach ($Tool in @("pdflatex", "bibtex", "makeglossaries", "makeindex")) {
                Assert-Tool -Name $Tool
            }

            Invoke-Tool -Name "pdflatex" -Arguments @(
                $InstallerOption,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "$Main.tex"
            )
            Invoke-Tool -Name "bibtex" -Arguments @($Main)
            Invoke-Tool -Name "makeglossaries" -Arguments @($Main)
            Invoke-Tool -Name "makeindex" -Arguments @("$Main.idx")
            Invoke-Tool -Name "pdflatex" -Arguments @(
                $InstallerOption,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "$Main.tex"
            )
            Invoke-Tool -Name "pdflatex" -Arguments @(
                $InstallerOption,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "$Main.tex"
            )
        }
        "clean" {
            Assert-Tool -Name "latexmk"
            Invoke-Tool -Name "latexmk" -Arguments @("-c", "$Main.tex")

            foreach ($Extension in @(
                "acn", "acr", "alg", "bbl", "blg", "glg", "glo", "gls",
                "ist", "xdy"
            )) {
                $GeneratedFile = Join-Path $Root "$Main.$Extension"
                Remove-Item -Path $GeneratedFile -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
finally {
    Pop-Location
}
