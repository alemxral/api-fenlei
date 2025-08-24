#!/bin/bash

# Image Classification Automation Script for Linux/macOS
# This script sends images to the API classification service at scheduled times

# =============================================================================
# USER CONFIGURATION - MODIFY THESE VARIABLES
# =============================================================================

# Time to run the classification (24-hour format, e.g., "02:00" for 2 AM)
SCHEDULE_TIME="02:00"

# Path to the directory containing images to classify
IMAGES_PATH="/path/to/your/images"

# API endpoint configuration
# Set to "localhost" if running locally, or provide the web URL
API_MODE="localhost"  # Options: "localhost" or "web"
LOCAL_URL="http://localhost:5000"
WEB_URL="https://api-fenlei-production.up.railway.app"

# API parameters
TOP_K=5  # Number of top predictions to return
BATCH_SIZE=5  # Number of images to send per batch request

# Output directory for results
OUTPUT_DIR="./classification_results"

# Log file
LOG_FILE="./image_classification.log"

# =============================================================================
# SCRIPT LOGIC - DO NOT MODIFY UNLESS YOU KNOW WHAT YOU'RE DOING
# =============================================================================

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if API is available
check_api_availability() {
    local url="$1"
    if curl -s --connect-timeout 10 "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to determine API URL
get_api_url() {
    if [ "$API_MODE" = "localhost" ]; then
        if check_api_availability "$LOCAL_URL"; then
            echo "$LOCAL_URL"
        else
            log_message "WARNING: Local API not available, trying web URL"
            if check_api_availability "$WEB_URL"; then
                echo "$WEB_URL"
            else
                log_message "ERROR: Neither local nor web API is available"
                exit 1
            fi
        fi
    else
        if check_api_availability "$WEB_URL"; then
            echo "$WEB_URL"
        else
            log_message "ERROR: Web API is not available"
            exit 1
        fi
    fi
}

# Function to classify a single image
classify_single_image() {
    local image_path="$1"
    local api_url="$2"
    local filename=$(basename "$image_path")
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local output_file="$OUTPUT_DIR/${filename}_${timestamp}.json"
    
    log_message "Classifying single image: $filename"
    
    response=$(curl -s -X POST \
        -F "image=@$image_path" \
        "$api_url/api/classify?top_k=$TOP_K")
    
    if [ $? -eq 0 ]; then
        echo "$response" | jq '.' > "$output_file" 2>/dev/null
        if [ $? -eq 0 ]; then
            log_message "SUCCESS: Results saved to $output_file"
        else
            echo "$response" > "$output_file"
            log_message "SUCCESS: Results saved to $output_file (raw format)"
        fi
    else
        log_message "ERROR: Failed to classify $filename"
    fi
}

# Function to classify images in batch
classify_batch_images() {
    local images_array=("$@")
    local api_url="${images_array[0]}"
    unset 'images_array[0]'
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local output_file="$OUTPUT_DIR/batch_${timestamp}.json"
    
    log_message "Classifying batch of ${#images_array[@]} images"
    
    # Build curl command with multiple file uploads
    local curl_cmd="curl -s -X POST"
    for image in "${images_array[@]}"; do
        if [ -f "$image" ]; then
            curl_cmd="$curl_cmd -F \"images=@$image\""
        fi
    done
    curl_cmd="$curl_cmd \"$api_url/api/classify/batch?top_k=$TOP_K\""
    
    response=$(eval $curl_cmd)
    
    if [ $? -eq 0 ]; then
        echo "$response" | jq '.' > "$output_file" 2>/dev/null
        if [ $? -eq 0 ]; then
            log_message "SUCCESS: Batch results saved to $output_file"
        else
            echo "$response" > "$output_file"
            log_message "SUCCESS: Batch results saved to $output_file (raw format)"
        fi
    else
        log_message "ERROR: Failed to classify batch"
    fi
}

# Function to process images
process_images() {
    if [ ! -d "$IMAGES_PATH" ]; then
        log_message "ERROR: Images directory not found: $IMAGES_PATH"
        exit 1
    fi
    
    # Get API URL
    api_url=$(get_api_url)
    log_message "Using API URL: $api_url"
    
    # Find image files
    image_files=($(find "$IMAGES_PATH" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.webp" \) 2>/dev/null))
    
    if [ ${#image_files[@]} -eq 0 ]; then
        log_message "WARNING: No image files found in $IMAGES_PATH"
        exit 0
    fi
    
    log_message "Found ${#image_files[@]} image files"
    
    # Process images in batches
    local processed=0
    local batch=()
    
    for image in "${image_files[@]}"; do
        batch+=("$image")
        
        if [ ${#batch[@]} -eq $BATCH_SIZE ]; then
            classify_batch_images "$api_url" "${batch[@]}"
            batch=()
            processed=$((processed + BATCH_SIZE))
            
            # Small delay between batches to avoid overwhelming the API
            sleep 2
        fi
    done
    
    # Process remaining images in the last batch
    if [ ${#batch[@]} -gt 0 ]; then
        if [ ${#batch[@]} -eq 1 ]; then
            classify_single_image "${batch[0]}" "$api_url"
        else
            classify_batch_images "$api_url" "${batch[@]}"
        fi
        processed=$((processed + ${#batch[@]}))
    fi
    
    log_message "Completed processing $processed images"
}

# Function to install script as a cron job
install_cron() {
    local script_path="$(realpath "$0")"
    local cron_time=$(echo "$SCHEDULE_TIME" | sed 's/:/ /')
    local cron_entry="$cron_time * * * $script_path > /dev/null 2>&1"
    
    # Check if cron entry already exists
    if crontab -l 2>/dev/null | grep -q "$script_path"; then
        log_message "Cron job already exists for this script"
    else
        # Add cron entry
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        log_message "Cron job installed: Will run daily at $SCHEDULE_TIME"
        log_message "To remove: crontab -e and delete the line containing $script_path"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --run-now          Run classification immediately"
    echo "  --install-cron     Install as a daily cron job"
    echo "  --test-api         Test API connectivity"
    echo "  --help             Show this help message"
    echo ""
    echo "Configuration:"
    echo "  Edit the variables at the top of this script to configure:"
    echo "  - SCHEDULE_TIME: Time to run (default: $SCHEDULE_TIME)"
    echo "  - IMAGES_PATH: Path to images directory (default: $IMAGES_PATH)"
    echo "  - API_MODE: 'localhost' or 'web' (default: $API_MODE)"
    echo "  - LOCAL_URL: Local API URL (default: $LOCAL_URL)"
    echo "  - WEB_URL: Web API URL (default: $WEB_URL)"
}

# Function to test API connectivity
test_api() {
    log_message "Testing API connectivity..."
    
    if [ "$API_MODE" = "localhost" ]; then
        if check_api_availability "$LOCAL_URL"; then
            log_message "✓ Local API is available at $LOCAL_URL"
        else
            log_message "✗ Local API is not available at $LOCAL_URL"
        fi
    fi
    
    if check_api_availability "$WEB_URL"; then
        log_message "✓ Web API is available at $WEB_URL"
    else
        log_message "✗ Web API is not available at $WEB_URL"
    fi
}

# Main script logic
case "${1:-}" in
    --run-now)
        log_message "=== Starting image classification (manual run) ==="
        process_images
        log_message "=== Classification completed ==="
        ;;
    --install-cron)
        install_cron
        ;;
    --test-api)
        test_api
        ;;
    --help)
        show_usage
        ;;
    "")
        # Default behavior: run classification (for cron)
        log_message "=== Starting scheduled image classification ==="
        process_images
        log_message "=== Scheduled classification completed ==="
        ;;
    *)
        echo "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
