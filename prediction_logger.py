import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class PredictionLogger:
    def __init__(self, log_file_path: str = "prediction_history.json"):
        """Initialize the prediction logger with a JSON file path"""
        self.log_file_path = log_file_path
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Create the log file if it doesn't exist"""
        if not os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, 'w') as f:
                    json.dump([], f)
                logger.info(f"Created new prediction log file: {self.log_file_path}")
            except Exception as e:
                logger.error(f"Error creating log file: {str(e)}")
    
    def log_prediction(self, 
                      filename: str, 
                      predictions: List[Dict[str, Any]], 
                      request_type: str = "single",
                      user_ip: Optional[str] = None,
                      processing_time: Optional[float] = None) -> bool:
        """
        Log a prediction result to the JSON file
        
        Args:
            filename: Name of the uploaded file
            predictions: List of prediction results
            request_type: Type of request ("single" or "batch")
            user_ip: IP address of the user (optional)
            processing_time: Time taken to process in seconds (optional)
            
        Returns:
            Boolean indicating success
        """
        try:
            # Read existing logs
            logs = self.read_logs()
            
            # Create new log entry
            log_entry = {
                "id": len(logs) + 1,
                "timestamp": datetime.now().isoformat(),
                "filename": secure_filename(filename) if filename else "unknown",
                "request_type": request_type,
                "top_prediction": {
                    "class_name": predictions[0]["class_name"] if predictions else "unknown",
                    "confidence": predictions[0]["confidence"] if predictions else 0.0,
                    "confidence_percentage": predictions[0]["confidence_percentage"] if predictions else "0.00%"
                },
                "total_predictions": len(predictions),
                "all_predictions": predictions[:3],  # Store top 3 predictions only
                "user_ip": user_ip,
                "processing_time": processing_time,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S")
            }
            
            # Add to logs
            logs.append(log_entry)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(logs) > 1000:
                logs = logs[-1000:]
                # Update IDs to maintain sequence
                for i, log in enumerate(logs):
                    log["id"] = i + 1
            
            # Write back to file
            with open(self.log_file_path, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info(f"Logged prediction for {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging prediction: {str(e)}")
            return False
    
    def log_batch_predictions(self, 
                            batch_results: List[Dict[str, Any]], 
                            user_ip: Optional[str] = None,
                            processing_time: Optional[float] = None) -> bool:
        """
        Log batch prediction results
        
        Args:
            batch_results: List of batch prediction results
            user_ip: IP address of the user (optional)
            processing_time: Total processing time in seconds (optional)
            
        Returns:
            Boolean indicating success
        """
        try:
            success_count = 0
            
            for result in batch_results:
                if result.get("status") == "success":
                    filename = f"batch_image_{result.get('image_index', 0) + 1}"
                    predictions = result.get("predictions", [])
                    
                    # Log each successful prediction in the batch
                    if self.log_prediction(
                        filename=filename,
                        predictions=predictions,
                        request_type="batch",
                        user_ip=user_ip,
                        processing_time=processing_time
                    ):
                        success_count += 1
            
            logger.info(f"Logged {success_count} batch predictions")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error logging batch predictions: {str(e)}")
            return False
    
    def read_logs(self) -> List[Dict[str, Any]]:
        """Read all logs from the JSON file"""
        try:
            with open(self.log_file_path, 'r') as f:
                logs = json.load(f)
                return logs if isinstance(logs, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        except Exception as e:
            logger.error(f"Error reading logs: {str(e)}")
            return []
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the most recent logs"""
        logs = self.read_logs()
        return logs[-limit:] if logs else []
    
    def get_logs_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get logs for a specific date (YYYY-MM-DD format)"""
        logs = self.read_logs()
        return [log for log in logs if log.get("date") == date]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the predictions"""
        logs = self.read_logs()
        
        if not logs:
            return {
                "total_predictions": 0,
                "today_predictions": 0,
                "most_common_class": "N/A",
                "average_confidence": 0.0,
                "single_requests": 0,
                "batch_requests": 0
            }
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_logs = [log for log in logs if log.get("date") == today]
        
        # Calculate statistics
        total_predictions = len(logs)
        today_predictions = len(today_logs)
        
        # Most common predicted class
        class_counts = {}
        confidence_sum = 0
        single_requests = 0
        batch_requests = 0
        
        for log in logs:
            class_name = log.get("top_prediction", {}).get("class_name", "unknown")
            confidence = log.get("top_prediction", {}).get("confidence", 0.0)
            request_type = log.get("request_type", "single")
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            confidence_sum += confidence
            
            if request_type == "single":
                single_requests += 1
            else:
                batch_requests += 1
        
        most_common_class = max(class_counts.items(), key=lambda x: x[1])[0] if class_counts else "N/A"
        average_confidence = confidence_sum / total_predictions if total_predictions > 0 else 0.0
        
        return {
            "total_predictions": total_predictions,
            "today_predictions": today_predictions,
            "most_common_class": most_common_class,
            "average_confidence": round(average_confidence * 100, 2),
            "single_requests": single_requests,
            "batch_requests": batch_requests
        }
    
    def clear_logs(self) -> bool:
        """Clear all logs (use with caution)"""
        try:
            with open(self.log_file_path, 'w') as f:
                json.dump([], f)
            logger.info("Cleared all prediction logs")
            return True
        except Exception as e:
            logger.error(f"Error clearing logs: {str(e)}")
            return False

# Global logger instance
prediction_logger = PredictionLogger()