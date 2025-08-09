# PowerShell script to test the Image Classification API

param(
    [Parameter(Mandatory=$true)]
    [string]$ImagePath,

    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = "http://localhost:5000",

    [Parameter(Mandatory=$false)]
    [int]$TopK = 5
)

# Function to test API health
function Test-ApiHealth {
    param([string]$BaseUrl)

    Write-Host "Checking API health..." -ForegroundColor Yellow

    try {
        $healthResponse = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method GET
        Write-Host "✓ API Status: $($healthResponse.status)" -ForegroundColor Green
        Write-Host "✓ Model: $($healthResponse.model)" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ API Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to classify a single image
function Invoke-ImageClassification {
    param(
        [string]$ImagePath,
        [string]$BaseUrl,
        [int]$TopK
    )

    # Check if image file exists
    if (-not (Test-Path $ImagePath)) {
        Write-Host "✗ Error: Image file not found at '$ImagePath'" -ForegroundColor Red
        return
    }

    # Get file info.
    $fileInfo = Get-Item $ImagePath
    $fileName = $fileInfo.Name
    $fileSize = [math]::Round($fileInfo.Length / 1MB, 2)

    Write-Host "`nImage Details:" -ForegroundColor Cyan
    Write-Host "  File: $fileName"
    Write-Host "  Size: $fileSize MB"
    Write-Host "  Path: $ImagePath"

    # Check file size (16MB limit)
    if ($fileInfo.Length -gt 16777216) {
        Write-Host "✗ Error: File size exceeds 16MB limit" -ForegroundColor Red
        return
    }

    # Prepare the multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"

    # Read file as bytes
    $fileBytes = [System.IO.File]::ReadAllBytes($ImagePath)
    $fileContentType = "image/*"

    # Build form data
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"image`"; filename=`"$fileName`"",
        "Content-Type: $fileContentType$LF",
        [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes),
        "--$boundary--$LF"
    ) -join $LF

    # Convert to bytes
    $bodyBytes = [System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($bodyLines)

    # Prepare headers
    $headers = @{
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }

    Write-Host "`nSending classification request..." -ForegroundColor Yellow

    try {
        # Make the API request
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/classify?top_k=$TopK" -Method POST -Body $bodyBytes -Headers $headers

        # Display results
        Write-Host "`n" + "="*50 -ForegroundColor Green
        Write-Host "CLASSIFICATION RESULTS" -ForegroundColor Green
        Write-Host "="*50 -ForegroundColor Green

        Write-Host "`nStatus: $($response.status)" -ForegroundColor Green
        Write-Host "File: $($response.filename)"
        Write-Host "Total Predictions: $($response.total_predictions)"

        Write-Host "`nTop Predictions:" -ForegroundColor Cyan
        Write-Host "-" * 40

        for ($i = 0; $i -lt $response.predictions.Length; $i++) {
            $pred = $response.predictions[$i]
            $rank = $i + 1
            $confidence = [math]::Round($pred.confidence * 100, 2)

            # Color code confidence levels
            $color = if ($confidence -ge 50) { "Green" }
                    elseif ($confidence -ge 20) { "Yellow" }
                    else { "Red" }

            Write-Host "$rank. " -NoNewline
            Write-Host "$($pred.class_name)" -ForegroundColor White -NoNewline
            Write-Host " - " -NoNewline
            Write-Host "$confidence%" -ForegroundColor $color

            # Create visual confidence bar
            $barLength = [math]::Floor($confidence / 5)
            $bar = "█" * $barLength + "░" * (20 - $barLength)
            Write-Host "   [$bar] $($pred.confidence_percentage)" -ForegroundColor DarkGray
        }

        Write-Host "`n" + "="*50 -ForegroundColor Green

        # Export results to JSON file
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $outputFile = "classification_result_$timestamp.json"
        $response | ConvertTo-Json -Depth 3 | Out-File -FilePath $outputFile -Encoding UTF8
        Write-Host "`nResults saved to: $outputFile" -ForegroundColor Cyan

    }
    catch {
        Write-Host "`n✗ Classification Failed:" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red

        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode.value__
            Write-Host "  Status Code: $statusCode" -ForegroundColor Red

            try {
                $errorStream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorStream)
                $errorBody = $reader.ReadToEnd()
                $errorJson = $errorBody | ConvertFrom-Json
                Write-Host "  Server Message: $($errorJson.message)" -ForegroundColor Red
            }
            catch {
                Write-Host "  Could not parse error response" -ForegroundColor Red
            }
        }
    }
}

# Function to get API information
function Get-ApiInfo {
    param([string]$BaseUrl)

    try {
        $infoResponse = Invoke-RestMethod -Uri "$BaseUrl/api/info" -Method GET

        Write-Host "`nAPI Information:" -ForegroundColor Cyan
        Write-Host "  Name: $($infoResponse.api_name)"
        Write-Host "  Version: $($infoResponse.version)"
        Write-Host "  Model: $($infoResponse.model)"
        Write-Host "  Max File Size: $($infoResponse.limits.max_file_size)"
        Write-Host "  Max Batch Size: $($infoResponse.limits.max_batch_size)"
    }
    catch {
        Write-Host "Could not retrieve API information" -ForegroundColor Yellow
    }
}

# Main execution
Write-Host "Image Classification API Test Script" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta

# Test API health first
if (Test-ApiHealth -BaseUrl $ApiUrl) {

    # Get API info
    Get-ApiInfo -BaseUrl $ApiUrl

    # Classify the image
    Invoke-ImageClassification -ImagePath $ImagePath -BaseUrl $ApiUrl -TopK $TopK

} else {
    Write-Host "`nCannot proceed with classification - API is not healthy" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  1. The API URL is correct: $ApiUrl" -ForegroundColor Yellow
    Write-Host "  2. The server is running" -ForegroundColor Yellow
    Write-Host "  3. No firewall blocking the connection" -ForegroundColor Yellow
}

Write-Host "`nScript completed." -ForegroundColor Magenta