# Image Classification API Dependencies
# Copy this content to requirements.txt when running locally

# Flask web framework and related packages
Flask>=3.1.1
Werkzeug>=3.1.3

# Machine Learning packages
tensorflow>=2.16.0,<2.18.0
numpy>=1.24.0,<2.0.0
Pillow>=9.0.0

# Database support (optional - already included in project)
Flask-SQLAlchemy>=3.1.1
psycopg2-binary>=2.9.10

# Email validation (optional - already included in project)
email-validator>=2.2.0

# Production server
gunicorn>=23.0.0

# Installation instructions:
# For local development:
# pip install -r requirements.txt
#
# For virtual environment:
# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate
# pip install -r requirements.txt
#
# To run the application locally:
# python main.py
# or
# gunicorn --bind 0.0.0.0:5000 main:app