// Image Classification App JavaScript

class ImageClassificationApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.init();
    }

    init() {
        this.checkApiHealth();
        this.setupEventListeners();
        this.loadPredictionHistory();
    }

    setupEventListeners() {
        // Single image upload
        document.getElementById('single-upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSingleImageUpload();
        });

        // Batch image upload
        document.getElementById('batch-upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleBatchImageUpload();
        });

        // Image preview for single upload
        document.getElementById('single-image').addEventListener('change', (e) => {
            this.previewSingleImage(e.target.files[0]);
        });

        // Batch image count
        document.getElementById('batch-images').addEventListener('change', (e) => {
            this.updateBatchCount(e.target.files.length);
        });

        // History tab event listeners
        document.getElementById('refresh-history-btn').addEventListener('click', () => {
            this.loadPredictionHistory();
        });

        document.getElementById('load-history-btn').addEventListener('click', () => {
            this.loadPredictionHistory();
        });

        document.getElementById('clear-history-btn').addEventListener('click', () => {
            this.clearPredictionHistory();
        });

        // Tab switch event listener
        document.getElementById('history-tab').addEventListener('shown.bs.tab', () => {
            this.loadPredictionHistory();
        });
    }

    async checkApiHealth() {
        const statusElement = document.getElementById('api-status');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();

            if (response.ok && data.status === 'healthy') {
                statusElement.innerHTML = `
                    <i class="fas fa-check-circle text-success me-2"></i>
                    <span class="status-healthy">API is healthy - ${data.model} model loaded</span>
                `;
            } else {
                throw new Error(data.message || 'API is not healthy');
            }
        } catch (error) {
            statusElement.innerHTML = `
                <i class="fas fa-exclamation-triangle text-danger me-2"></i>
                <span class="status-unhealthy">API is not available: ${error.message}</span>
            `;
        }
    }

    previewSingleImage(file) {
        const previewContainer = document.getElementById('single-preview');
        const previewImg = document.getElementById('single-preview-img');

        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                previewContainer.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            previewContainer.style.display = 'none';
        }
    }

    updateBatchCount(count) {
        const batchCount = document.getElementById('batch-count');
        const batchCountText = document.getElementById('batch-count-text');

        if (count > 0) {
            batchCountText.textContent = `${count} image${count > 1 ? 's' : ''} selected`;
            batchCount.style.display = 'block';
            
            if (count > 10) {
                batchCountText.innerHTML = `
                    <span class="text-warning">
                        ${count} images selected (max 10 allowed)
                    </span>
                `;
            }
        } else {
            batchCount.style.display = 'none';
        }
    }

    async handleSingleImageUpload() {
        const form = document.getElementById('single-upload-form');
        const submitBtn = document.getElementById('single-submit-btn');
        const fileInput = document.getElementById('single-image');
        const topK = document.getElementById('single-top-k').value;

        if (!fileInput.files[0]) {
            this.showError('Please select an image file');
            return;
        }

        // Set loading state
        this.setLoadingState(submitBtn, true);

        try {
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            const response = await fetch(`${this.apiBaseUrl}/classify?top_k=${topK}`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.displaySingleResult(data);
            } else {
                throw new Error(data.message || 'Classification failed');
            }
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleBatchImageUpload() {
        const form = document.getElementById('batch-upload-form');
        const submitBtn = document.getElementById('batch-submit-btn');
        const fileInput = document.getElementById('batch-images');
        const topK = document.getElementById('batch-top-k').value;

        if (!fileInput.files.length) {
            this.showError('Please select image files');
            return;
        }

        if (fileInput.files.length > 10) {
            this.showError('Maximum 10 images allowed per batch');
            return;
        }

        // Set loading state
        this.setLoadingState(submitBtn, true);

        try {
            const formData = new FormData();
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append('images', fileInput.files[i]);
            }

            const response = await fetch(`${this.apiBaseUrl}/classify/batch?top_k=${topK}`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.displayBatchResults(data);
            } else {
                throw new Error(data.message || 'Batch classification failed');
            }
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    displaySingleResult(data) {
        const container = document.getElementById('results-container');
        
        const resultHtml = `
            <div class="card result-card fade-in">
                <div class="card-header">
                    <h6 class="mb-0">
                        <i class="fas fa-image me-2"></i>
                        Classification Results - ${data.filename}
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        ${data.predictions.map((pred, index) => `
                            <div class="col-md-6 mb-3">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <strong>${pred.class_name}</strong>
                                    <span class="badge bg-primary">${pred.confidence_percentage}</span>
                                </div>
                                <div class="confidence-bar bg-dark">
                                    <div class="confidence-fill" style="width: ${pred.confidence * 100}%"></div>
                                </div>
                                <small class="text-muted">Confidence: ${(pred.confidence * 100).toFixed(2)}%</small>
                            </div>
                        `).join('')}
                    </div>
                    <div class="mt-3 text-muted">
                        <small>
                            <i class="fas fa-clock me-1"></i>
                            Generated at ${new Date().toLocaleTimeString()}
                        </small>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = resultHtml;
    }

    displayBatchResults(data) {
        const container = document.getElementById('results-container');
        
        let resultHtml = `
            <div class="card batch-result-card fade-in">
                <div class="card-header">
                    <h6 class="mb-0">
                        <i class="fas fa-images me-2"></i>
                        Batch Classification Results
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="text-center">
                                <h5 class="text-primary">${data.total_images}</h5>
                                <small class="text-muted">Total Images</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <h5 class="text-success">${data.valid_images}</h5>
                                <small class="text-muted">Successfully Processed</small>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <h5 class="text-warning">${data.invalid_images}</h5>
                                <small class="text-muted">Failed</small>
                            </div>
                        </div>
                    </div>
        `;

        // Display results for each image
        if (data.results && data.results.length > 0) {
            resultHtml += '<div class="row">';
            
            data.results.forEach((result, index) => {
                if (result.status === 'success') {
                    resultHtml += `
                        <div class="col-lg-6 mb-4">
                            <div class="card">
                                <div class="card-header">
                                    <small class="text-muted">Image ${result.image_index + 1}</small>
                                </div>
                                <div class="card-body">
                                    ${result.predictions.slice(0, 3).map(pred => `
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span>${pred.class_name}</span>
                                            <span class="badge bg-primary">${pred.confidence_percentage}</span>
                                        </div>
                                        <div class="confidence-bar bg-dark mb-2">
                                            <div class="confidence-fill" style="width: ${pred.confidence * 100}%"></div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    resultHtml += `
                        <div class="col-lg-6 mb-4">
                            <div class="card error-card">
                                <div class="card-header">
                                    <small class="text-muted">Image ${result.image_index + 1}</small>
                                </div>
                                <div class="card-body">
                                    <div class="text-danger">
                                        <i class="fas fa-exclamation-triangle me-2"></i>
                                        Error: ${result.error}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }
            });
            
            resultHtml += '</div>';
        }

        // Display invalid files if any
        if (data.invalid_files && data.invalid_files.length > 0) {
            resultHtml += `
                <div class="mt-3">
                    <h6 class="text-warning">Invalid Files:</h6>
                    <ul class="list-group list-group-flush">
                        ${data.invalid_files.map(file => `
                            <li class="list-group-item bg-transparent">
                                <strong>${file.filename}</strong> - ${file.error}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        resultHtml += `
                    <div class="mt-3 text-muted">
                        <small>
                            <i class="fas fa-clock me-1"></i>
                            Generated at ${new Date().toLocaleTimeString()}
                        </small>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = resultHtml;
    }

    showError(message) {
        const container = document.getElementById('results-container');
        container.innerHTML = `
            <div class="alert alert-danger fade-in" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Processing...
            `;
        } else {
            button.disabled = false;
            const icon = button.id.includes('single') ? 'upload' : 'upload';
            const text = button.id.includes('single') ? 'Classify Image' : 'Classify Images';
            button.innerHTML = `
                <i class="fas fa-${icon} me-2"></i>
                ${text}
            `;
        }
    }

    async loadPredictionHistory() {
        const tableBody = document.getElementById('history-table-body');
        const limit = document.getElementById('history-limit').value;
        
        // Show loading state
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    <i class="fas fa-spinner fa-spin me-2"></i>
                    Loading prediction history...
                </td>
            </tr>
        `;

        try {
            const response = await fetch(`${this.apiBaseUrl}/logs?limit=${limit}`);
            const data = await response.json();

            if (response.ok) {
                this.displayPredictionHistory(data.logs);
                this.updateStatistics(data.statistics);
            } else {
                throw new Error(data.message || 'Failed to load history');
            }
        } catch (error) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error loading history: ${error.message}
                    </td>
                </tr>
            `;
        }
    }

    displayPredictionHistory(logs) {
        const tableBody = document.getElementById('history-table-body');

        if (!logs || logs.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="fas fa-info-circle me-2"></i>
                        No prediction history available
                    </td>
                </tr>
            `;
            return;
        }

        // Sort logs by ID descending (newest first)
        logs.sort((a, b) => b.id - a.id);

        const tableRows = logs.map(log => {
            const timestamp = new Date(log.timestamp).toLocaleString();
            const processingTime = log.processing_time ? `${(log.processing_time * 1000).toFixed(0)}ms` : 'N/A';
            const userIp = log.user_ip || 'N/A';
            const confidence = log.top_prediction.confidence_percentage || '0.00%';
            
            // Color code confidence
            let confidenceClass = 'text-danger';
            const confValue = parseFloat(confidence);
            if (confValue >= 70) confidenceClass = 'text-success';
            else if (confValue >= 40) confidenceClass = 'text-warning';

            // Color code request type
            const typeClass = log.request_type === 'single' ? 'badge bg-primary' : 'badge bg-info';

            return `
                <tr>
                    <td>#${log.id}</td>
                    <td>
                        <small>${timestamp}</small>
                    </td>
                    <td>
                        <span class="text-truncate" style="max-width: 150px; display: inline-block;" 
                              title="${log.filename}">
                            ${log.filename}
                        </span>
                    </td>
                    <td>
                        <span class="${typeClass}">${log.request_type}</span>
                    </td>
                    <td>
                        <strong>${log.top_prediction.class_name}</strong>
                    </td>
                    <td>
                        <span class="${confidenceClass}">
                            <strong>${confidence}</strong>
                        </span>
                    </td>
                    <td>
                        <small class="text-muted">${processingTime}</small>
                    </td>
                    <td>
                        <small class="text-muted">${userIp}</small>
                    </td>
                </tr>
            `;
        }).join('');

        tableBody.innerHTML = tableRows;
    }

    updateStatistics(stats) {
        if (!stats) return;

        document.getElementById('stat-total').textContent = stats.total_predictions || '0';
        document.getElementById('stat-today').textContent = stats.today_predictions || '0';
        document.getElementById('stat-single').textContent = stats.single_requests || '0';
        document.getElementById('stat-batch').textContent = stats.batch_requests || '0';
        document.getElementById('stat-confidence').textContent = `${stats.average_confidence || 0}%`;
        document.getElementById('stat-common').textContent = stats.most_common_class || 'N/A';
    }

    async clearPredictionHistory() {
        if (!confirm('Are you sure you want to clear all prediction history? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/logs/clear`, {
                method: 'POST'
            });

            const data = await response.json();

            if (response.ok) {
                // Reload the history to show empty state
                this.loadPredictionHistory();
                
                // Show success message
                const tableBody = document.getElementById('history-table-body');
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Prediction history cleared successfully
                        </td>
                    </tr>
                `;

                // Reset statistics
                this.updateStatistics({
                    total_predictions: 0,
                    today_predictions: 0,
                    single_requests: 0,
                    batch_requests: 0,
                    average_confidence: 0,
                    most_common_class: 'N/A'
                });

                // Reload after a short delay
                setTimeout(() => {
                    this.loadPredictionHistory();
                }, 2000);

            } else {
                throw new Error(data.message || 'Failed to clear history');
            }
        } catch (error) {
            alert(`Error clearing history: ${error.message}`);
        }
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ImageClassificationApp();
});
