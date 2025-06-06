# NeuroScan Docker Validation Script
# This script validates the complete Docker setup

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    switch ($Status) {
        "SUCCESS" { Write-Host "[$timestamp] ✓ $Message" -ForegroundColor Green }
        "ERROR"   { Write-Host "[$timestamp] ✗ $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "[$timestamp] ⚠ $Message" -ForegroundColor Yellow }
        default   { Write-Host "[$timestamp] ℹ $Message" -ForegroundColor Cyan }
    }
}

function Test-DockerInstallation {
    Write-Status "Checking Docker installation..."
    
    try {
        $dockerVersion = docker --version
        Write-Status "Docker found: $dockerVersion" "SUCCESS"
        return $true
    } catch {
        Write-Status "Docker not found or not running" "ERROR"
        return $false
    }
}

function Test-DockerCompose {
    Write-Status "Checking Docker Compose..."
    
    try {
        $composeVersion = docker-compose --version
        Write-Status "Docker Compose found: $composeVersion" "SUCCESS"
        return $true
    } catch {
        Write-Status "Docker Compose not found" "ERROR"
        return $false
    }
}

function Test-DockerFiles {
    Write-Status "Validating Docker configuration files..."
    
    $requiredFiles = @(
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "docker-compose.dev.yml",
        "docker-compose.test.yml",
        "BackendAPI\Dockerfile",
        "BackendAPI\Dockerfile.dev", 
        "WebFrontend\Dockerfile",
        "WebFrontend\Dockerfile.dev",
        ".env.example",
        ".dockerignore"
    )
    
    $allFilesExist = $true
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Status "Found: $file" "SUCCESS"
        } else {
            Write-Status "Missing: $file" "ERROR"
            $allFilesExist = $false
        }
    }
    
    return $allFilesExist
}

function Test-EnvFile {
    Write-Status "Checking environment configuration..."
    
    if (Test-Path ".env") {
        Write-Status "Environment file exists" "SUCCESS"
        
        # Check for required variables
        $envContent = Get-Content ".env" -Raw
        $requiredVars = @(
            "POSTGRES_PASSWORD",
            "JWT_SECRET_KEY",
            "REDIS_PASSWORD"
        )
        
        foreach ($var in $requiredVars) {
            if ($envContent -match "$var=.+") {
                Write-Status "Found required variable: $var" "SUCCESS"
            } else {
                Write-Status "Missing or empty variable: $var" "WARNING"
            }
        }
        
        return $true
    } else {
        Write-Status "Environment file not found. Creating from template..." "WARNING"
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Status "Created .env from template. Please edit it!" "SUCCESS"
        }
        return $false
    }
}

function Test-DockerComposeValidation {
    Write-Status "Validating Docker Compose configurations..."
    
    $configs = @(
        "docker-compose.yml",
        "docker-compose.prod.yml", 
        "docker-compose.dev.yml",
        "docker-compose.test.yml"
    )
    
    $allValid = $true
    
    foreach ($config in $configs) {
        if (Test-Path $config) {
            try {
                $result = docker-compose -f $config config --quiet 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Status "Valid configuration: $config" "SUCCESS"
                } else {
                    Write-Status "Invalid configuration: $config - $result" "ERROR"
                    $allValid = $false
                }
            } catch {
                Write-Status "Error validating: $config - $($_.Exception.Message)" "ERROR"
                $allValid = $false
            }
        }
    }
    
    return $allValid
}

function Test-DockerBuild {
    Write-Status "Testing Docker builds..."
    
    try {
        Write-Status "Building backend image..."
        $buildResult = docker build -t neuroscan-backend-test ./BackendAPI 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Backend build successful" "SUCCESS"
        } else {
            Write-Status "Backend build failed: $buildResult" "ERROR"
            return $false
        }
        
        Write-Status "Building frontend image..."
        $buildResult = docker build -t neuroscan-frontend-test ./WebFrontend 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Frontend build successful" "SUCCESS"
        } else {
            Write-Status "Frontend build failed: $buildResult" "ERROR"
            return $false
        }
        
        return $true
    } catch {
        Write-Status "Build test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-NetworkConnectivity {
    Write-Status "Testing network connectivity..."
    
    try {
        # Start a minimal test environment
        docker-compose -f docker-compose.test.yml up -d postgres-test redis-test 2>$null
        Start-Sleep 10
        
        # Test database connectivity
        $dbTest = docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready 2>&1
        if ($LASTEXITCODE -eq 0 -and $dbTest -match "accepting connections") {
            Write-Status "Database connectivity test passed" "SUCCESS"
            $dbSuccess = $true
        } else {
            Write-Status "Database connectivity test failed: $dbTest" "ERROR"
            $dbSuccess = $false
        }
        
        # Test Redis connectivity
        $redisTest = docker-compose -f docker-compose.test.yml exec -T redis-test redis-cli ping 2>&1
        if ($redisTest -match "PONG") {
            Write-Status "Redis connectivity test passed" "SUCCESS"
            $redisSuccess = $true
        } else {
            Write-Status "Redis connectivity test failed: $redisTest" "ERROR"
            $redisSuccess = $false
        }
        
        # Cleanup
        docker-compose -f docker-compose.test.yml down -v 2>$null
          return ($dbSuccess -and $redisSuccess)
        
    } catch {
        Write-Status "Network connectivity test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-ManagementScripts {
    Write-Status "Checking management scripts..."
    
    $scripts = @(
        "docker.ps1",
        "docker.bat",
        "scripts\backup.sh",
        "scripts\health-check.sh"
    )
    
    $allExist = $true
    
    foreach ($script in $scripts) {
        if (Test-Path $script) {
            Write-Status "Found script: $script" "SUCCESS"
        } else {
            Write-Status "Missing script: $script" "ERROR"
            $allExist = $false
        }
    }
    
    return $allExist
}

function Show-Summary {
    param([hashtable]$Results)
    
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "NeuroScan Docker Validation Summary" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
    
    $passed = 0
    $total = $Results.Count
    
    foreach ($test in $Results.GetEnumerator()) {
        if ($test.Value) {
            Write-Status "$($test.Key): PASSED" "SUCCESS"
            $passed++
        } else {
            Write-Status "$($test.Key): FAILED" "ERROR"
        }
    }
    
    Write-Host "`nOverall Result: $passed/$total tests passed" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
    
    if ($passed -eq $total) {
        Write-Status "🎉 All Docker components are properly configured!" "SUCCESS"
        Write-Host "`nNext steps:" -ForegroundColor Green
        Write-Host "1. Run: .\docker.ps1 setup" -ForegroundColor White
        Write-Host "2. Access frontend: http://localhost:3000" -ForegroundColor White
        Write-Host "3. Access backend API: http://localhost:8000/docs" -ForegroundColor White
    } else {
        Write-Status "⚠️  Some issues found. Please fix them before proceeding." "WARNING"
    }
}

# Main validation process
Write-Host "NeuroScan Docker Validation Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$results = @{}

# Run all tests
$results["Docker Installation"] = Test-DockerInstallation
$results["Docker Compose"] = Test-DockerCompose
$results["Docker Files"] = Test-DockerFiles
$results["Environment Configuration"] = Test-EnvFile
$results["Compose Validation"] = Test-DockerComposeValidation
$results["Management Scripts"] = Test-ManagementScripts

# Only run build and network tests if basic components are working
if ($results["Docker Installation"] -and $results["Docker Compose"] -and $results["Docker Files"]) {
    $results["Docker Build"] = Test-DockerBuild
    $results["Network Connectivity"] = Test-NetworkConnectivity
}

# Show summary
Show-Summary -Results $results

Write-Host "`nValidation completed at $(Get-Date)" -ForegroundColor Cyan
