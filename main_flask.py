"""
Flask-only entry point for Gunicorn compatibility
Author: Alejandro Moral Aranda
"""

from app import app

# Export app for Gunicorn
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)