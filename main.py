"""
Main entry point with Flask/Streamlit fallback support
Author: Alejandro Moral Aranda
"""

import os
import sys

# Export app for Gunicorn compatibility
try:
    from app import app
    application = app  # Gunicorn looks for 'application'
except ImportError:
    application = None

def main():
    """Main entry point - try Flask first, fallback to Streamlit"""
    # Check if we should force a specific framework
    force_streamlit = os.getenv('FORCE_STREAMLIT', '').lower() in ['true', '1', 'yes']
    
    if force_streamlit:
        # Force Streamlit mode
        from app_launcher import run_streamlit_app
        return run_streamlit_app()
    
    # Default behavior: try Flask first
    try:
        from app import app
        
        # Try to start Flask
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        
        print(f"🌶️ Starting Flask server on {host}:{port}")
        app.run(host=host, port=port, debug=True)
        
    except Exception as e:
        print(f"❌ Flask failed: {str(e)}")
        print("🔄 Falling back to Streamlit...")
        
        try:
            from app_launcher import run_streamlit_app
            return run_streamlit_app()
        except Exception as streamlit_error:
            print(f"❌ Streamlit also failed: {str(streamlit_error)}")
            print("💡 Try setting FORCE_STREAMLIT=true environment variable")
            sys.exit(1)

if __name__ == "__main__":
    main()
