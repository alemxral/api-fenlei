# Image Classification Automation Script for Windows
# This script sends images to the API classification service at scheduled times

# =============================================================================
# USER CONFIGURATION - MODIFY THESE VARIABLES
# =============================================================================

# Time to run the classification (24-hour format, e.g., "02:00" for 2 AM)
$SCHEDULE_TIME = "02:00"

# Path to the directory containing images to classify
$IMAGES_PATH = "C:\path\to\your\images"

# API endpoint configuration
# Set to "localhost" if running locally, or provide the web URL
$API_MODE = "localhost"  # Options: "localhost" or "web"
$LOCAL_URL = "http://localhost:5000"
$WEB_URL = "https://api-fenlei-production.up.railway.app"

# API parameters
$TOP_K = 5  # Number of top predictions to return
$BATCH_SIZE = 5  # Number of images to send per batch request

# Output directory for results
$OUTPUT_DIR = ".\classification_results"

# Log file
$LOG_FILE = ".\image_classification.log"

# =============================================================================
# SCRIPT LOGIC - DO NOT MODIFY UNLESS YOU KNOW WHAT YOU'RE DOING
# =============================================================================

# Create output directory if it doesn't exist
if (!(Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR -Force | Out-Null
}

# Function to log messages with timestamp
function Log-Message {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $LOG_FILE -Value $logEntry
}

# Function to check if API is available
function Test-ApiAvailability {
    param($Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10 -UseBasicParsing
        return $true
    }
    catch {
        return $false
    }
}

# Function to determine API URL
function Get-ApiUrl {
    if ($API_MODE -eq "localhost") {
        if (Test-ApiAvailability $LOCAL_URL) {
            return $LOCAL_URL
        }
        else {
            Log-Message "WARNING: Local API not available, trying web URL"
            if (Test-ApiAvailability $WEB_URL) {
                return $WEB_URL
            }
            else {
                Log-Message "ERROR: Neither local nor web API is available"
                exit 1
            }
        }
    }
    else {
        if (Test-ApiAvailability $WEB_URL) {
            return $WEB_URL
        }
        else {
            Log-Message "ERROR: Web API is not available"
            exit 1
        }
    }
}

# Function to classify a single image
function Invoke-SingleImageClassification {
    param($ImagePath, $ApiUrl)
    
    $filename = Split-Path $ImagePath -Leaf
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outputFile = Join-Path $OUTPUT_DIR "${filename}_${timestamp}.json"
    
    Log-Message "Classifying single image: $filename"
    
    try {
        # Create multipart form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $fileBytes = [System.IO.File]::ReadAllBytes($ImagePath)
        $encoding = [System.Text.Encoding]::GetEncoding("iso-8859-1")
        
        $bodyStart = @"
--$boundary
Content-Disposition: form-data; name="image"; filename="$filename"
Content-Type: application/octet-stream

"@
        
        $bodyEnd = @"

--$boundary--
"@
        
        $bodyStartBytes = $encoding.GetBytes($bodyStart)
        $bodyEndBytes = $encoding.GetBytes($bodyEnd)
        
        $bodyBytes = $bodyStartBytes + $fileBytes + $bodyEndBytes
        
        $headers = @{
            'Content-Type' = "multipart/form-data; boundary=$boundary"
        }
        
        $response = Invoke-RestMethod -Uri "$ApiUrl/api/classify?top_k=$TOP_K" -Method POST -Body $bodyBytes -Headers $headers
        
        # Save response to file
        $response | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
        Log-Message "SUCCESS: Results saved to $outputFile"
    }
    catch {
        Log-Message "ERROR: Failed to classify $filename - $($_.Exception.Message)"
    }
}

# Function to classify images in batch
function Invoke-BatchImageClassification {
    param($ImagePaths, $ApiUrl)
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outputFile = Join-Path $OUTPUT_DIR "batch_$timestamp.json"
    
    Log-Message "Classifying batch of $($ImagePaths.Count) images"
    
    try {
        # Create multipart form data for batch
        $boundary = [System.Guid]::NewGuid().ToString()
        $encoding = [System.Text.Encoding]::GetEncoding("iso-8859-1")
        
        $bodyParts = @()
        
        foreach ($imagePath in $ImagePaths) {
            if (Test-Path $imagePath) {
                $filename = Split-Path $imagePath -Leaf
                $fileBytes = [System.IO.File]::ReadAllBytes($imagePath)
                
                $partStart = @"
--$boundary
Content-Disposition: form-data; name="images"; filename="$filename"
Content-Type: application/octet-stream

"@
                $partStartBytes = $encoding.GetBytes($partStart)
                $bodyParts += $partStartBytes + $fileBytes + $encoding.GetBytes("`r`n")
            }
        }
        
        $bodyEnd = "--$boundary--`r`n"
        $bodyEndBytes = $encoding.GetBytes($bodyEnd)
        
        $bodyBytes = [byte[]]::new(0)
        foreach ($part in $bodyParts) {
            $bodyBytes += $part
        }
        $bodyBytes += $bodyEndBytes
        
        $headers = @{
            'Content-Type' = "multipart/form-data; boundary=$boundary"
        }
        
        $response = Invoke-RestMethod -Uri "$ApiUrl/api/classify/batch?top_k=$TOP_K" -Method POST -Body $bodyBytes -Headers $headers
        
        # Save response to file
        $response | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
        Log-Message "SUCCESS: Batch results saved to $outputFile"
    }
    catch {
        Log-Message "ERROR: Failed to classify batch - $($_.Exception.Message)"
    }
}

# Function to process images
function Start-ImageProcessing {
    if (!(Test-Path $IMAGES_PATH)) {
        Log-Message "ERROR: Images directory not found: $IMAGES_PATH"
        exit 1
    }
    
    # Get API URL
    $apiUrl = Get-ApiUrl
    Log-Message "Using API URL: $apiUrl"
    
    # Find image files
    $imageExtensions = @("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.webp")
    $imageFiles = @()
    
    foreach ($extension in $imageExtensions) {
        $imageFiles += Get-ChildItem -Path $IMAGES_PATH -Filter $extension -File -Recurse
    }
    
    if ($imageFiles.Count -eq 0) {
        Log-Message "WARNING: No image files found in $IMAGES_PATH"
        return
    }
    
    Log-Message "Found $($imageFiles.Count) image files"
    
    # Process images in batches
    $processed = 0
    $batch = @()
    
    foreach ($image in $imageFiles) {
        $batch += $image.FullName
        
        if ($batch.Count -eq $BATCH_SIZE) {
            Invoke-BatchImageClassification -ImagePaths $batch -ApiUrl $apiUrl
            $batch = @()
            $processed += $BATCH_SIZE
            
            # Small delay between batches to avoid overwhelming the API
            Start-Sleep -Seconds 2
        }
    }
    
    # Process remaining images in the last batch
    if ($batch.Count -gt 0) {
        if ($batch.Count -eq 1) {
            Invoke-SingleImageClassification -ImagePath $batch[0] -ApiUrl $apiUrl
        }
        else {
            Invoke-BatchImageClassification -ImagePaths $batch -ApiUrl $apiUrl
        }
        $processed += $batch.Count
    }
    
    Log-Message "Completed processing $processed images"
}

# Function to install script as a scheduled task
function Install-ScheduledTask {
    $scriptPath = $MyInvocation.ScriptName
    $taskName = "ImageClassificationAutomation"
    
    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Log-Message "Scheduled task already exists: $taskName"
        return
    }
    
    try {
        # Create scheduled task action
        $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$scriptPath`" -RunNow"
        
        # Create scheduled task trigger (daily at specified time)
        $trigger = New-ScheduledTaskTrigger -Daily -At $SCHEDULE_TIME
        
        # Create scheduled task settings
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        
        # Register the scheduled task
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Automated image classification using API"
        
        Log-Message "Scheduled task installed: Will run daily at $SCHEDULE_TIME"
        Log-Message "To remove: Run 'Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false'"
    }
    catch {
        Log-Message "ERROR: Failed to install scheduled task - $($_.Exception.Message)"
    }
}

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\image_classifier_automation.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -RunNow          Run classification immediately"
    Write-Host "  -InstallTask     Install as a daily scheduled task"
    Write-Host "  -TestApi         Test API connectivity"
    Write-Host "  -Help            Show this help message"
    Write-Host ""
    Write-Host "Configuration:"
    Write-Host "  Edit the variables at the top of this script to configure:"
    Write-Host "  - SCHEDULE_TIME: Time to run (default: $SCHEDULE_TIME)"
    Write-Host "  - IMAGES_PATH: Path to images directory (default: $IMAGES_PATH)"
    Write-Host "  - API_MODE: 'localhost' or 'web' (default: $API_MODE)"
    Write-Host "  - LOCAL_URL: Local API URL (default: $LOCAL_URL)"
    Write-Host "  - WEB_URL: Web API URL (default: $WEB_URL)"
}

# Function to test API connectivity
function Test-Api {
    Log-Message "Testing API connectivity..."
    
    if ($API_MODE -eq "localhost") {
        if (Test-ApiAvailability $LOCAL_URL) {
            Log-Message "✓ Local API is available at $LOCAL_URL"
        }
        else {
            Log-Message "✗ Local API is not available at $LOCAL_URL"
        }
    }
    
    if (Test-ApiAvailability $WEB_URL) {
        Log-Message "✓ Web API is available at $WEB_URL"
    }
    else {
        Log-Message "✗ Web API is not available at $WEB_URL"
    }
}

# Parameter handling
param(
    [switch]$RunNow,
    [switch]$InstallTask,
    [switch]$TestApi,
    [switch]$Help
)

# Main script logic
if ($Help) {
    Show-Usage
}
elseif ($RunNow) {
    Log-Message "=== Starting image classification (manual run) ==="
    Start-ImageProcessing
    Log-Message "=== Classification completed ==="
}
elseif ($InstallTask) {
    Install-ScheduledTask
}
elseif ($TestApi) {
    Test-Api
}
else {
    # Default behavior: run classification (for scheduled task)
    Log-Message "=== Starting scheduled image classification ==="
    Start-ImageProcessing
    Log-Message "=== Scheduled classification completed ==="
}
