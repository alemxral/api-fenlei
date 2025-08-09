"""
Streamlit version of the Image Classification API
Author: Alejandro Moral Aranda
Project: DLBDSMTP01 – Task 2: Image classification for a refund department
"""

import streamlit as st
import time
import json
import os
from datetime import datetime
from PIL import Image
import numpy as np

# Import our ML classifier and utilities
from ml_classifier import classifier
from utils import validate_image_file
from prediction_logger import prediction_logger

# Page configuration
st.set_page_config(
    page_title="Image Classification API - Streamlit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Load custom CSS for better styling"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .project-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .stats-container {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .prediction-result {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #28a745;
        margin: 1rem 0;
    }
    
    .footer {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 8px;
        margin-top: 3rem;
        border-top: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """Display the main header with project information"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Image Classification API</h1>
        <p>Upload images to classify them using a pre-trained MobileNetV2 model</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="project-info">
        <h3>🎓 Academic Project Information</h3>
        <p><strong>Subject:</strong> DLBDSMTP01 – Project: From Model to Production</p>
        <p><strong>Task:</strong> Task 2: Image classification for a refund department (spotlight: Batch processing)</p>
        <p><strong>Author:</strong> <span style="color: #007bff;"><strong>Alejandro Moral Aranda</strong></span></p>
    </div>
    """, unsafe_allow_html=True)

def display_api_status():
    """Display API status check"""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                # Test if classifier is loaded
                if hasattr(classifier, 'model') and classifier.model is not None:
                    st.success("✅ ML Model loaded and ready!")
                else:
                    st.warning("⚠️ ML Model loading...")
            except Exception as e:
                st.error(f"❌ Model Error: {str(e)}")

def process_single_image(uploaded_file, top_k=5):
    """Process a single uploaded image"""
    try:
        # Validate the file
        validation_result = validate_image_file(uploaded_file)
        if not validation_result["valid"]:
            st.error(f"❌ {validation_result['error']}")
            return None
        
        # Display the image
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
        
        # Classify the image
        start_time = time.time()
        predictions = classifier.classify_image(uploaded_file, top_k=top_k)
        processing_time = time.time() - start_time
        
        # Log the prediction
        prediction_logger.log_prediction(
            filename=uploaded_file.name,
            predictions=predictions,
            request_type="single",
            user_ip="streamlit-user",
            processing_time=processing_time
        )
        
        return {
            "predictions": predictions,
            "processing_time": processing_time,
            "filename": uploaded_file.name
        }
        
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
        return None

def process_batch_images(uploaded_files, top_k=5):
    """Process multiple uploaded images"""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))
        
        try:
            # Validate the file
            validation_result = validate_image_file(uploaded_file)
            if not validation_result["valid"]:
                results.append({
                    "filename": uploaded_file.name,
                    "error": validation_result["error"],
                    "status": "error"
                })
                continue
            
            # Classify the image
            start_time = time.time()
            predictions = classifier.classify_image(uploaded_file, top_k=top_k)
            processing_time = time.time() - start_time
            
            # Log the prediction
            prediction_logger.log_prediction(
                filename=uploaded_file.name,
                predictions=predictions,
                request_type="batch",
                user_ip="streamlit-user",
                processing_time=processing_time
            )
            
            results.append({
                "filename": uploaded_file.name,
                "predictions": predictions,
                "processing_time": processing_time,
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "filename": uploaded_file.name,
                "error": str(e),
                "status": "error"
            })
    
    status_text.text("✅ Batch processing complete!")
    progress_bar.progress(1.0)
    return results

def display_predictions(result):
    """Display prediction results"""
    if not result or "predictions" not in result or not result["predictions"]:
        return
    
    st.markdown(f"""
    <div class="prediction-result">
        <h3>📊 Classification Results for: {result['filename']}</h3>
        <p><strong>Processing time:</strong> {result['processing_time']*1000:.0f}ms</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display predictions in a table
    predictions_data = []
    for i, pred in enumerate(result['predictions'], 1):
        predictions_data.append({
            "Rank": i,
            "Class": pred['class_name'].replace('_', ' ').title(),
            "Confidence": pred['confidence_percentage'],
            "Score": f"{pred['confidence']:.4f}"
        })
    
    st.dataframe(predictions_data, use_container_width=True)

def display_batch_results(results):
    """Display batch processing results"""
    if not results:
        return
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Images", len(results))
    with col2:
        st.metric("Successful", len(successful))
    with col3:
        st.metric("Failed", len(failed))
    
    # Display successful results
    if successful:
        st.subheader("✅ Successful Classifications")
        for result in successful:
            with st.expander(f"📊 {result['filename']} - {result['predictions'][0]['class_name']} ({result['predictions'][0]['confidence_percentage']})"):
                display_predictions(result)
    
    # Display failed results
    if failed:
        st.subheader("❌ Failed Classifications")
        for result in failed:
            st.error(f"**{result['filename']}**: {result['error']}")

def display_prediction_history():
    """Display prediction history and statistics"""
    st.header("📋 Prediction History")
    
    # Get statistics
    stats = prediction_logger.get_statistics()
    
    # Display statistics
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Predictions", stats['total_predictions'])
    with col2:
        st.metric("Today", stats['today_predictions'])
    with col3:
        st.metric("Avg Confidence", f"{stats['average_confidence']}%")
    with col4:
        st.metric("Most Common", stats['most_common_class'][:15] + "..." if len(stats['most_common_class']) > 15 else stats['most_common_class'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # History controls
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔄 Refresh History"):
            st.rerun()
    with col2:
        limit = st.selectbox("Show entries", [25, 50, 100, 500], index=1)
    
    # Get and display history
    logs = prediction_logger.get_recent_logs(limit)
    
    if logs:
        # Prepare data for display
        history_data = []
        for log in reversed(logs):  # Show newest first
            history_data.append({
                "ID": f"#{log['id']}",
                "Timestamp": datetime.fromisoformat(log['timestamp']).strftime("%Y-%m-%d %H:%M:%S"),
                "Filename": log['filename'][:20] + "..." if len(log['filename']) > 20 else log['filename'],
                "Type": log['request_type'],
                "Prediction": log['top_prediction']['class_name'].replace('_', ' ').title(),
                "Confidence": log['top_prediction']['confidence_percentage'],
                "Time (ms)": f"{log['processing_time']*1000:.0f}" if log['processing_time'] else "N/A"
            })
        
        st.dataframe(history_data, use_container_width=True)
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            if prediction_logger.clear_logs():
                st.success("✅ History cleared successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to clear history")
    else:
        st.info("📭 No prediction history available yet. Upload some images to get started!")

def display_footer():
    """Display footer with project information"""
    st.markdown("""
    <div class="footer">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
            <div>
                <h4>🎓 Academic Project Information</h4>
                <p><strong>Subject Code:</strong> DLBDSMTP01</p>
                <p><strong>Subject Name:</strong> Project: From Model to Production</p>
                <p><strong>Assignment:</strong> Task 2: Image classification for a refund department</p>
                <p><strong>Focus:</strong> Batch processing implementation</p>
            </div>
            <div>
                <h4>👨‍💻 Project Author</h4>
                <p><strong style="color: #007bff;">Alejandro Moral Aranda</strong></p>
                <p><strong>Technology Stack:</strong> Flask/Streamlit, TensorFlow, MobileNetV2</p>
                <p><strong>Features:</strong> Single/Batch Classification, Prediction History</p>
            </div>
        </div>
        <hr>
        <div style="text-align: center; color: #6c757d;">
            <small>© 2025 Alejandro Moral Aranda | Academic Project - DLBDSMTP01 | Built with Streamlit & TensorFlow</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    # Load custom CSS
    load_custom_css()
    
    # Display header
    display_header()
    
    # Display API status
    display_api_status()
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("🚀 Navigation")
        page = st.radio("Select Page", ["🖼️ Image Classification", "📋 Prediction History"])
        
        if page == "🖼️ Image Classification":
            st.header("⚙️ Settings")
            top_k = st.slider("Number of predictions", min_value=1, max_value=10, value=5)
            
            st.header("📊 Quick Stats")
            stats = prediction_logger.get_statistics()
            st.metric("Total Predictions", stats['total_predictions'])
            st.metric("Today", stats['today_predictions'])
    
    # Main content area
    if page == "🖼️ Image Classification":
        st.header("🖼️ Image Classification")
        
        # Tab selection
        tab1, tab2 = st.tabs(["📷 Single Image", "📁 Batch Processing"])
        
        with tab1:
            st.subheader("Upload a Single Image")
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
                accept_multiple_files=False
            )
            
            if uploaded_file is not None:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("🔍 Classify Image", type="primary"):
                        with st.spinner("Classifying image..."):
                            result = process_single_image(uploaded_file, top_k)
                            if result:
                                with col2:
                                    display_predictions(result)
        
        with tab2:
            st.subheader("Upload Multiple Images")
            uploaded_files = st.file_uploader(
                "Choose image files (up to 10)",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                if len(uploaded_files) > 10:
                    st.warning("⚠️ Maximum 10 files allowed. Only first 10 will be processed.")
                    uploaded_files = uploaded_files[:10]
                
                st.info(f"📁 Selected {len(uploaded_files)} files")
                
                if st.button("🔍 Classify All Images", type="primary"):
                    with st.spinner("Processing batch..."):
                        results = process_batch_images(uploaded_files, top_k)
                        display_batch_results(results)
    
    elif page == "📋 Prediction History":
        display_prediction_history()
    
    # Display footer
    display_footer()

if __name__ == "__main__":
    main()