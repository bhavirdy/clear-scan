document.addEventListener('DOMContentLoaded', function () {
    // ClearScan Medical Image Upload and Analysis Functionality
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const resultsSection = document.getElementById('resultsSection');

    if (uploadForm && fileInput) {
        // Drag and drop functionality
        const uploadArea = document.getElementById('uploadArea');

        if (uploadArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, unhighlight, false);
            });

            function highlight() {
                uploadArea.classList.add('drag-over');
            }

            function unhighlight() {
                uploadArea.classList.remove('drag-over');
            }

            uploadArea.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;

                if (files.length > 0) {
                    fileInput.files = files;
                    handleFileSelection(files[0]);
                }
            }
        }

        // File input change handler
        fileInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                handleFileSelection(file);
            }
        });

        function handleFileSelection(file) {
            clearResultsForNewUpload();
            hideError();

            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff'];
            if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.dcm')) {
                showError('Please select a valid medical image file (PNG, JPEG, BMP, TIFF, or DICOM)');
                return;
            }

            const maxSize = 50 * 1024 * 1024; // 50MB
            if (file.size > maxSize) {
                showError('File size is too large. Please select a file smaller than 50MB.');
                return;
            }

            if (fileName && fileSize && fileInfo) {
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                fileInfo.classList.remove('d-none');

                const analyzeBtn = document.getElementById('analyzeBtn');
                if (analyzeBtn) {
                    analyzeBtn.disabled = false;
                }
            }
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        let isAnalyzing = false;

        uploadForm.addEventListener('submit', function (event) {
            event.preventDefault();

            if (isAnalyzing) {
                console.log('Analysis already in progress...');
                return;
            }

            if (!fileInput.files || fileInput.files.length === 0) {
                showError('Please select a medical image first');
                return;
            }

            analyzeImage();
        });

        function analyzeImage() {
            if (isAnalyzing) return;
            isAnalyzing = true;

            const formData = new FormData(uploadForm);
            const submitBtn = uploadForm.querySelector('button[type="submit"]');

            hideError();
            showProgressIndicator();

            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
                submitBtn.disabled = true;
            }

            fetch('/process', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Analysis response:', data);

                    if (data.prediction || data.status === 'success') {
                        displayResults(data);
                    } else {
                        showError(data.error || 'Analysis failed');
                    }
                })
                .catch(error => {
                    console.error('Analysis error:', error);
                    showError(`Network error: ${error.message}`);
                })
                .finally(() => {
                    if (submitBtn) {
                        submitBtn.innerHTML = '<i class="fas fa-microscope me-2"></i>Analyze Image';
                        submitBtn.disabled = false;
                    }
                    hideProgressIndicator();
                    isAnalyzing = false;
                });
        }

        function showProgressIndicator() {
            const progress = document.createElement('div');
            progress.id = 'analysisProgress';
            progress.className = 'progress mt-3';
            progress.innerHTML = `
                <div class="progress-bar progress-bar-striped progress-bar-animated analysis-progress" 
                     role="progressbar" style="width: 100%">
                    AI Analysis in Progress...
                </div>
            `;
            uploadForm.appendChild(progress);
        }

        function hideProgressIndicator() {
            const progress = document.getElementById('analysisProgress');
            if (progress) {
                progress.remove();
            }
        }

        function displayResults(data) {
            console.log('Displaying results with data:', data);

            if (!resultsSection) {
                console.error('Results section not found in DOM');
                return;
            }

            const analysisResults = document.getElementById('analysisResults');
            if (!analysisResults) {
                console.error('analysisResults element not found in DOM');
                return;
            }

            hideError();
            resultsSection.classList.remove('d-none');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

            let resultsHTML = `
                <div class="alert alert-success">
                    <h5 class="alert-heading fw-bold"><i class="fas fa-check-circle me-2"></i>Analysis Complete</h5>
                    <p class="mb-0">Medical image analysis has been completed successfully.</p>
                </div>
            `;

            if (data.prediction) {
                const confidence = data.confidence ? (data.confidence * 100).toFixed(1) : '0';
                const confidenceClass = confidence > 70 ? 'success' : confidence > 40 ? 'warning' : 'danger';

                resultsHTML += `
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card border-primary">
                                <div class="card-header bg-primary text-white">
                                    <h6 class="mb-0"><i class="fas fa-diagnoses me-2"></i>AI Diagnosis</h6>
                                </div>
                                <div class="card-body text-center">
                                    <h4 class="text-primary">${data.prediction.toUpperCase()}</h4>
                                    <div class="progress mt-3 mb-2">
                                        <div class="progress-bar bg-${confidenceClass}" style="width: ${confidence}%"></div>
                                    </div>
                                    <p class="mb-0"><strong>Confidence:</strong> <span class="text-${confidenceClass}">${confidence}%</span></p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card border-info">
                                <div class="card-header bg-info text-white">
                                    <h6 class="mb-0"><i class="fas fa-image me-2"></i>GradCAM Visualization</h6>
                                </div>
                                <div class="card-body text-center">
                                    ${data.gradcam_image_url ?
                        `<img src="${data.gradcam_image_url}" class="img-fluid rounded" alt="GradCAM Heatmap" style="max-height: 200px;">
                                             <p class="mt-2 text-muted">Areas of focus highlighted</p>` :
                        `<div class="text-muted">
                                                <i class="fas fa-image fa-3x mb-2"></i>
                                                <p>Visualization not available</p>
                                             </div>`
                    }
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }

            resultsHTML += `
                <div class="alert alert-info mt-3">
                    <h6 class="alert-heading"><i class="fas fa-info-circle me-2"></i>Medical Disclaimer</h6>
                    <p class="mb-0">This AI analysis is for diagnostic assistance only and should not replace professional medical judgment.</p>
                </div>

               
            `;

            analysisResults.innerHTML = resultsHTML;
            const exportBtn = document.getElementById('exportReportBtn');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => {
                    console.log("Export button clicked!");
                    alert("This will trigger PDF export flow once patient info is collected.");
                });
            }
        }

        function showError(message) {
            hideProgressIndicator();

            const existingError = uploadForm.querySelector('.alert-danger');
            if (existingError) {
                existingError.remove();
            }

            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
            errorDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Error:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            uploadForm.appendChild(errorDiv);
            errorDiv.scrollIntoView({ behavior: 'smooth' });

            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 8000);
        }

        function hideError() {
            const existingError = uploadForm.querySelector('.alert-danger');
            if (existingError) {
                existingError.remove();
            }
        }

        function hideResults() {
            console.log('hideResults called - results will be hidden');
            if (resultsSection) {
                resultsSection.classList.add('d-none');
                const analysisResults = document.getElementById('analysisResults');
                if (analysisResults) {
                    analysisResults.innerHTML = '';
                }
            }
        }

        function clearResultsForNewUpload() {
            hideResults();
        }
    }

    // Multi-step registration form functionality
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        const steps = signupForm.querySelectorAll('.step');
        const nextBtns = signupForm.querySelectorAll('.nextBtn');
        const prevBtns = signupForm.querySelectorAll('.prevBtn');
        let currentStep = 0;

        function showStep(step) {
            steps.forEach((s, index) => {
                s.style.display = index === step ? 'block' : 'none';
            });
        }

        nextBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                if (validateCurrentStep()) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });

        prevBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                currentStep--;
                showStep(currentStep);
            });
        });

        function validateCurrentStep() {
            const currentStepElement = steps[currentStep];
            const requiredFields = currentStepElement.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            return isValid;
        }

        const password = document.getElementById('inputPassword');
        const confirmPassword = document.getElementById('inputConfirmPassword');

        if (password && confirmPassword) {
            function validatePasswords() {
                if (password.value !== confirmPassword.value) {
                    confirmPassword.setCustomValidity('Passwords do not match');
                } else {
                    confirmPassword.setCustomValidity('');
                }
            }

            password.addEventListener('input', validatePasswords);
            confirmPassword.addEventListener('input', validatePasswords);
        }
    }
});
