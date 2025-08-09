"""
Universal App Launcher - Flask with Streamlit Fallback
Author: Alejandro Moral Aranda
Project: DLBDSMTP01 – Task 2: Image classification for a refund department

This script attempts to run Flask first, and falls back to Streamlit if Flask fails.
"""

import sys
import os
import subprocess
import time
import logging
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = ['flask', 'streamlit', 'tensorflow', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Please install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def try_flask_import() -> bool:
    """Try to import Flask app components"""
    try:
        from app import app
        from ml_classifier import classifier
        logger.info("✅ Flask app imports successful")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Flask import failed: {str(e)}")
        return False

def try_streamlit_import() -> bool:
    """Try to import Streamlit app components"""
    try:
        import streamlit as st
        from ml_classifier import classifier
        logger.info("✅ Streamlit imports successful")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Streamlit import failed: {str(e)}")
        return False

def run_flask_app(host='0.0.0.0', port=5000) -> bool:
    """Attempt to run the Flask application"""
    try:
        logger.info("🚀 Starting Flask application...")
        
        # Try to import Flask app first
        if not try_flask_import():
            return False
        
        # Try to run with Gunicorn first (production-like)
        try:
            logger.info("Attempting to start with Gunicorn...")
            result = subprocess.run([
                'gunicorn', 
                '--bind', f'{host}:{port}',
                '--reuse-port',
                '--reload',
                'main:app'
            ], check=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Gunicorn not available or failed, trying Flask dev server...")
            
            # Fallback to Flask development server
            try:
                from app import app
                app.run(host=host, port=port, debug=True)
                return True
            except Exception as e:
                logger.error(f"❌ Flask dev server failed: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Flask startup failed: {str(e)}")
        return False

def run_streamlit_app() -> bool:
    """Run the Streamlit application"""
    try:
        logger.info("🚀 Starting Streamlit application...")
        
        # Check if Streamlit imports work
        if not try_streamlit_import():
            return False
        
        # Run Streamlit
        streamlit_cmd = [
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app.py',
            '--server.address', '0.0.0.0',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ]
        
        logger.info("Starting Streamlit server...")
        subprocess.run(streamlit_cmd, check=True)
        return True
        
    except Exception as e:
        logger.error(f"❌ Streamlit startup failed: {str(e)}")
        return False

def display_startup_info():
    """Display startup information"""
    print("\n" + "="*60)
    print("🧠 IMAGE CLASSIFICATION API LAUNCHER")
    print("="*60)
    print("📚 Project: DLBDSMTP01 – From Model to Production")
    print("📝 Task 2: Image classification for refund department")
    print("👨‍💻 Author: Alejandro Moral Aranda")
    print("="*60)
    print("🎯 Attempting to start with Flask first...")
    print("🔄 Will fallback to Streamlit if Flask fails")
    print("="*60 + "\n")

def main():
    """Main launcher function"""
    display_startup_info()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependencies check failed. Exiting.")
        return False
    
    # Get environment variables for configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    force_streamlit = os.getenv('FORCE_STREAMLIT', '').lower() in ['true', '1', 'yes']
    
    if force_streamlit:
        logger.info("🎯 FORCE_STREAMLIT=true, skipping Flask and running Streamlit")
        return run_streamlit_app()
    
    # Try Flask first
    logger.info("🌶️ Attempting to start Flask application...")
    try:
        # Quick test to see if Flask can start
        if try_flask_import():
            logger.info(f"🌶️ Flask ready! Starting server on {host}:{port}")
            
            # For production environments, prefer Gunicorn
            if os.getenv('FLASK_ENV') != 'development':
                try:
                    os.execvp('gunicorn', [
                        'gunicorn', 
                        '--bind', f'{host}:{port}',
                        '--reuse-port',
                        '--reload',
                        'main:app'
                    ])
                except FileNotFoundError:
                    logger.info("Gunicorn not found, using Flask dev server")
            
            # Use Flask development server
            from app import app
            logger.info(f"🌶️ Starting Flask development server on http://{host}:{port}")
            app.run(host=host, port=port, debug=True)
            return True
            
    except KeyboardInterrupt:
        logger.info("👋 Flask server stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Flask failed to start: {str(e)}")
        logger.info("🔄 Falling back to Streamlit...")
    
    # Fallback to Streamlit
    logger.info("🎈 Starting Streamlit as fallback...")
    try:
        return run_streamlit_app()
    except KeyboardInterrupt:
        logger.info("👋 Streamlit server stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Both Flask and Streamlit failed!")
        logger.error(f"Flask error: Check logs above")
        logger.error(f"Streamlit error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("❌ Application failed to start with both Flask and Streamlit")
        sys.exit(1)