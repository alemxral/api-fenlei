# Image Classification Automation Scripts

This repository contains automation scripts for both Linux/macOS (Bash) and Windows (PowerShell) that automatically send images to your image classification API at scheduled times.

## Features

- **Automatic scheduling**: Run image classification at specified times daily
- **Smart API detection**: Automatically detects if local API is running, falls back to web API
- **Batch processing**: Efficiently processes multiple images in batches
- **Comprehensive logging**: Detailed logs with timestamps for monitoring
- **Error handling**: Robust error handling and recovery
- **Flexible configuration**: Easy-to-modify user-defined settings

## Files

- `image_classifier_automation.sh` - Linux/macOS Bash script
- `image_classifier_automation.ps1` - Windows PowerShell script

## Configuration

Both scripts have user-configurable variables at the top:

### Key Settings

- **SCHEDULE_TIME**: Time to run classification (24-hour format, e.g., "02:00" for 2 AM)
- **IMAGES_PATH**: Path to directory containing images to classify
- **API_MODE**: Set to "localhost" or "web"
- **LOCAL_URL**: Local API URL (default: http://localhost:5000)
- **WEB_URL**: Web API URL (https://api-fenlei-production.up.railway.app)
- **TOP_K**: Number of top predictions to return (default: 5)
- **BATCH_SIZE**: Number of images to send per batch request (default: 5)

### Example Configuration

```bash
# Linux/macOS (Bash)
SCHEDULE_TIME="02:00"
IMAGES_PATH="/home/user/Pictures/to_classify"
API_MODE="localhost"  # or "web"
```

```powershell
# Windows (PowerShell)
$SCHEDULE_TIME = "02:00"
$IMAGES_PATH = "C:\Users\YourName\Pictures\to_classify"
$API_MODE = "localhost"  # or "web"
```

## Linux/macOS Usage (Bash)

### Prerequisites

- `curl` command-line tool
- `jq` for JSON formatting (optional, but recommended)
- Bash shell

### Installation

1. Make the script executable:
```bash
chmod +x image_classifier_automation.sh
```

2. Edit the configuration variables at the top of the script

### Usage Options

```bash
# Test API connectivity
./image_classifier_automation.sh --test-api

# Run classification immediately
./image_classifier_automation.sh --run-now

# Install as daily cron job
./image_classifier_automation.sh --install-cron

# Show help
./image_classifier_automation.sh --help
```

### Setting up Automatic Scheduling

Use the built-in cron installation:
```bash
./image_classifier_automation.sh --install-cron
```

Or manually add to crontab:
```bash
crontab -e
# Add this line (replace with your actual script path and desired time):
0 2 * * * /path/to/image_classifier_automation.sh
```

## Windows Usage (PowerShell)

### Prerequisites

- PowerShell 5.0 or later
- Internet connection for web API access

### Installation

1. Open PowerShell as Administrator (for scheduled task installation)
2. Edit the configuration variables at the top of the script
3. Set execution policy if needed:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Usage Options

```powershell
# Test API connectivity
.\image_classifier_automation.ps1 -TestApi

# Run classification immediately
.\image_classifier_automation.ps1 -RunNow

# Install as daily scheduled task
.\image_classifier_automation.ps1 -InstallTask

# Show help
.\image_classifier_automation.ps1 -Help
```

### Setting up Automatic Scheduling

Use the built-in scheduled task installation:
```powershell
.\image_classifier_automation.ps1 -InstallTask
```

Or manually create a scheduled task:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Daily at desired time
4. Set action to start PowerShell with arguments: `-File "C:\path\to\image_classifier_automation.ps1"`

## API Endpoints Used

The scripts automatically detect and use the appropriate API endpoint:

- **Single Image**: `POST /api/classify`
- **Batch Images**: `POST /api/classify/batch`

### Supported Image Formats

- JPG/JPEG
- PNG
- GIF
- BMP
- WEBP

## Output

### Result Files

Results are saved in the `classification_results` directory:
- Single images: `{filename}_{timestamp}.json`
- Batch results: `batch_{timestamp}.json`

### Log Files

Detailed logs are saved to `image_classification.log` with timestamps.

### Example Output Structure

```json
{
  "status": "success",
  "filename": "example.jpg",
  "predictions": [
    {
      "class": "cat",
      "confidence": 0.95
    },
    {
      "class": "dog",
      "confidence": 0.03
    }
  ],
  "total_predictions": 5
}
```

## API Mode Selection

The scripts intelligently choose the API endpoint:

1. **localhost mode**: Tries local API first, falls back to web API if local is unavailable
2. **web mode**: Uses only the web API

This ensures your automation works whether your local API is running or not.

## Monitoring and Troubleshooting

### Check Logs

```bash
# Linux/macOS
tail -f image_classification.log

# Windows
Get-Content -Path ".\image_classification.log" -Wait
```

### Common Issues

1. **Permission Denied**: Make sure scripts are executable (Linux/macOS) or execution policy allows scripts (Windows)
2. **API Not Available**: Check network connection and API status
3. **No Images Found**: Verify the IMAGES_PATH exists and contains supported image files
4. **Scheduling Not Working**: Check cron service (Linux/macOS) or Task Scheduler (Windows)

### Testing

Always test your configuration before setting up automation:

```bash
# Linux/macOS
./image_classifier_automation.sh --test-api
./image_classifier_automation.sh --run-now

# Windows
.\image_classifier_automation.ps1 -TestApi
.\image_classifier_automation.ps1 -RunNow
```

## Security Considerations

- Store scripts in secure locations with appropriate file permissions
- Consider using environment variables for sensitive configuration
- Monitor log files for any security-related issues
- Regularly update and review automation scripts

## Support

For issues with the scripts:
1. Check the log files for detailed error messages
2. Verify your configuration settings
3. Test API connectivity manually
4. Ensure all prerequisites are installed

## License

These automation scripts are provided as-is for use with the image classification API.
