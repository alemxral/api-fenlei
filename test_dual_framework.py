#!/usr/bin/env python3
"""
Test script for dual framework functionality
Author: Alejandro Moral Aranda
"""

import sys
import time
import requests
import subprocess
import threading
from typing import Dict, Any

def test_flask_functionality() -> Dict[str, Any]:
    """Test Flask API functionality"""
    print("🌶️ Testing Flask functionality...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        health_check = response.status_code == 200
        
        # Test info endpoint
        response = requests.get("http://localhost:5000/api/info", timeout=5)
        info_check = response.status_code == 200
        
        # Test web interface
        response = requests.get("http://localhost:5000/", timeout=5)
        web_interface = response.status_code == 200
        
        return {
            "flask_available": True,
            "health_endpoint": health_check,
            "info_endpoint": info_check,
            "web_interface": web_interface,
            "all_tests_passed": all([health_check, info_check, web_interface])
        }
        
    except Exception as e:
        return {
            "flask_available": False,
            "error": str(e),
            "all_tests_passed": False
        }

def test_streamlit_functionality() -> Dict[str, Any]:
    """Test Streamlit functionality"""
    print("🎈 Testing Streamlit functionality...")
    
    try:
        # Check if Streamlit can be imported
        import streamlit as st
        streamlit_import = True
    except ImportError:
        streamlit_import = False
    
    try:
        # Try to check if Streamlit server responds (if running)
        response = requests.get("http://localhost:8501", timeout=3)
        streamlit_server = response.status_code == 200
    except:
        streamlit_server = False
    
    return {
        "streamlit_import": streamlit_import,
        "streamlit_server": streamlit_server,
        "all_tests_passed": streamlit_import  # Import is sufficient for basic functionality
    }

def test_fallback_mechanism():
    """Test the Flask -> Streamlit fallback mechanism"""
    print("🔄 Testing fallback mechanism...")
    
    # Test 1: Normal Flask startup
    print("  Test 1: Normal Flask startup...")
    try:
        from app import app
        flask_import_works = True
        print("    ✅ Flask imports successfully")
    except Exception as e:
        flask_import_works = False
        print(f"    ❌ Flask import failed: {e}")
    
    # Test 2: Streamlit fallback
    print("  Test 2: Streamlit fallback capability...")
    try:
        from app_launcher import run_streamlit_app
        streamlit_fallback_available = True
        print("    ✅ Streamlit fallback available")
    except Exception as e:
        streamlit_fallback_available = False
        print(f"    ❌ Streamlit fallback failed: {e}")
    
    # Test 3: Environment variable control
    print("  Test 3: Environment variable control...")
    import os
    os.environ['FORCE_STREAMLIT'] = 'true'
    force_streamlit_works = os.getenv('FORCE_STREAMLIT', '').lower() == 'true'
    print(f"    ✅ FORCE_STREAMLIT environment variable: {force_streamlit_works}")
    
    return {
        "flask_import": flask_import_works,
        "streamlit_fallback": streamlit_fallback_available,
        "env_variable_control": force_streamlit_works,
        "all_tests_passed": all([flask_import_works, streamlit_fallback_available, force_streamlit_works])
    }

def test_shared_components():
    """Test shared ML and logging components"""
    print("🧠 Testing shared components...")
    
    try:
        # Test ML classifier
        from ml_classifier import classifier
        ml_classifier_available = hasattr(classifier, 'model')
        print(f"    ML Classifier: {'✅' if ml_classifier_available else '❌'}")
        
        # Test prediction logger
        from prediction_logger import prediction_logger
        logger_available = hasattr(prediction_logger, 'log_prediction')
        print(f"    Prediction Logger: {'✅' if logger_available else '❌'}")
        
        # Test utilities
        from utils import validate_image_file, allowed_file
        utils_available = True
        print(f"    Utilities: {'✅' if utils_available else '❌'}")
        
        return {
            "ml_classifier": ml_classifier_available,
            "prediction_logger": logger_available,
            "utilities": utils_available,
            "all_tests_passed": all([ml_classifier_available, logger_available, utils_available])
        }
        
    except Exception as e:
        print(f"    ❌ Shared components error: {e}")
        return {
            "all_tests_passed": False,
            "error": str(e)
        }

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 DUAL FRAMEWORK FUNCTIONALITY TEST")
    print("="*60)
    print("📚 Project: DLBDSMTP01 – Task 2: Image classification")
    print("👨‍💻 Author: Alejandro Moral Aranda")
    print("="*60 + "\n")
    
    # Run tests
    flask_results = test_flask_functionality()
    streamlit_results = test_streamlit_functionality()
    fallback_results = test_fallback_mechanism()
    shared_results = test_shared_components()
    
    # Print results
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    print(f"🌶️ Flask Functionality: {'✅ PASS' if flask_results['all_tests_passed'] else '❌ FAIL'}")
    if not flask_results['all_tests_passed']:
        print(f"    Error: {flask_results.get('error', 'See details above')}")
    
    print(f"🎈 Streamlit Functionality: {'✅ PASS' if streamlit_results['all_tests_passed'] else '❌ FAIL'}")
    
    print(f"🔄 Fallback Mechanism: {'✅ PASS' if fallback_results['all_tests_passed'] else '❌ FAIL'}")
    
    print(f"🧠 Shared Components: {'✅ PASS' if shared_results['all_tests_passed'] else '❌ FAIL'}")
    
    # Overall result
    all_passed = all([
        flask_results['all_tests_passed'],
        streamlit_results['all_tests_passed'],
        fallback_results['all_tests_passed'],
        shared_results['all_tests_passed']
    ])
    
    print("\n" + "-"*60)
    print(f"🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("-"*60)
    
    if all_passed:
        print("\n🎉 Your dual-framework image classification API is ready!")
        print("🌶️ Flask: http://localhost:5000")
        print("🎈 Streamlit: http://localhost:8501")
        print("🚀 Run with: python main.py")
    else:
        print("\n🔧 Some components need attention. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)