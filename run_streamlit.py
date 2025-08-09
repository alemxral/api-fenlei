"""
Streamlit runner script
Author: Alejandro Moral Aranda
"""

import subprocess
import sys

def run_streamlit():
    """Run the Streamlit app"""
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app.py',
            '--server.address', '0.0.0.0',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ], check=True)
    except Exception as e:
        print(f"Error running Streamlit: {e}")

if __name__ == "__main__":
    run_streamlit()