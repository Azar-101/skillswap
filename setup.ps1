
# ==========================================
# SKILLSWAP AUTOMATIC SETUP SCRIPT
# Windows 10 / Windows 11
# ==========================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "       SKILLSWAP SETUP WIZARD"
Write-Host "======================================" -ForegroundColor Cyan

# Check project directory
if (!(Test-Path "run.py") -or !(Test-Path ".env.example")) {
    Write-Host "ERROR: Open the SkillSwap project root folder." -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow

try {
    $pythonVersion = py -3.12 --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python 3.12 is missing. Install it first." -ForegroundColor Red
    exit 1
}

# Generate secure secret key
Write-Host "`nGenerating Flask secret key..." -ForegroundColor Yellow

$secretKey = py -3.12 -c "import secrets; print(secrets.token_hex(32))"

# Ask for MySQL password
Write-Host "`nEnter a strong password for the SkillSwap MySQL user." -ForegroundColor Yellow

$securePassword = Read-Host "MySQL application password" -AsSecureString

$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)

try {
    $dbPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}

if ([string]::IsNullOrWhiteSpace($dbPassword)) {
    Write-Host "Password cannot be empty." -ForegroundColor Red
    exit 1
}

# URL encode password
Add-Type -AssemblyName System.Web
$encodedPassword = [System.Uri]::EscapeDataString($dbPassword)

# Create environment file
Write-Host "`nCreating .env..." -ForegroundColor Yellow

$envContent = @"
SECRET_KEY=$secretKey
DATABASE_URL=mysql+pymysql://skillswap_user:$encodedPassword@localhost:3306/skillswap
FLASK_APP=run.py
FLASK_DEBUG=1

# Jitsi
JITSI_DOMAIN=meet.jit.si

# AI providers (optional)
OPENAI_API_KEY=
OPENAI_MODEL=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=
GROQ_API_KEY=
GROQ_MODEL=

# AI configuration
PLATFORM_AI_ENABLED=false
AI_ENCRYPTION_KEY=
"@

if (Test-Path ".env") {
    $overwrite = Read-Host ".env already exists. Replace it? (yes/no)"

    if ($overwrite -ne "yes") {
        Write-Host "Existing .env preserved." -ForegroundColor Yellow
        exit 0
    }
}

[System.IO.File]::WriteAllText(
    (Join-Path (Get-Location) ".env"),
    $envContent,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host ".env created successfully." -ForegroundColor Green

# Create MySQL setup SQL
Write-Host "`nCreating MySQL setup SQL..." -ForegroundColor Yellow

$sqlContent = @"
CREATE DATABASE IF NOT EXISTS skillswap;

CREATE USER IF NOT EXISTS 'skillswap_user'@'localhost'
IDENTIFIED BY 'REPLACE_WITH_YOUR_MYSQL_PASSWORD';

ALTER USER 'skillswap_user'@'localhost'
IDENTIFIED BY 'REPLACE_WITH_YOUR_MYSQL_PASSWORD';

GRANT ALL PRIVILEGES ON skillswap.*
TO 'skillswap_user'@'localhost';

FLUSH PRIVILEGES;
"@

$sqlContent = $sqlContent.Replace(
    "REPLACE_WITH_YOUR_MYSQL_PASSWORD",
    $dbPassword.Replace("\", "\\").Replace("'", "''")
)

[System.IO.File]::WriteAllText(
    (Join-Path (Get-Location) "setup_mysql.sql"),
    $sqlContent,
    [System.Text.UTF8Encoding]::new($false)
)

# Add .env to gitignore
Write-Host "`nProtecting environment file..." -ForegroundColor Yellow

if (!(Test-Path ".gitignore")) {
    New-Item ".gitignore" -ItemType File | Out-Null
}

$gitignore = Get-Content ".gitignore" -Raw

if ($gitignore -notmatch '(?m)^\.env$') {
    Add-Content ".gitignore" "`n.env"
}

Write-Host ".env protected in .gitignore." -ForegroundColor Green

# Create Python virtual environment if missing
Write-Host "`nChecking virtual environment..." -ForegroundColor Yellow

if (!(Test-Path ".venv")) {
    py -3.12 -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
}
else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow

& ".venv\Scripts\python.exe" -m pip install --upgrade pip

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependency installation failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "       SETUP FILES CREATED!"
Write-Host "======================================" -ForegroundColor Green

Write-Host "`nCreated:"
Write-Host "1. .env"
Write-Host "2. setup_mysql.sql"
Write-Host "3. .venv"
Write-Host "`nNEXT STEPS:"
Write-Host "1. Open setup_mysql.sql in MySQL Workbench."
Write-Host "2. Execute it using your MySQL administrator connection."
Write-Host "3. Activate the virtual environment:"
Write-Host "   .venv\Scripts\Activate.ps1"
Write-Host "4. Run your application:"
Write-Host "   python run.py"

Write-Host "`nIMPORTANT: Keep .env private!" -ForegroundColor Yellow
Write-Host "Your AI API keys can be configured later." -ForegroundColor Cyan
