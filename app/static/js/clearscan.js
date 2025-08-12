document.addEventListener('DOMContentLoaded', function() {
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

        // File input change handler
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                handleFileSelection(file);
            }
        });

        function handleFileSelection(file) {
            // Validate file type
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff'];
            if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.dcm')) {
                alert('Please select a valid medical image file (PNG, JPEG, BMP, TIFF, or DICOM)');
                return;
            }

            // Display file info
            if (fileName && fileSize && fileInfo) {
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                fileInfo.classList.remove('d-none');
                
                // Enable analyze button
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

        // Form submission handler
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            if (!fileInput.files || fileInput.files.length === 0) {
                alert('Please select a medical image first');
                return;
            }

            analyzeImage();
        });

        function analyzeImage() {
            const formData = new FormData(uploadForm);
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
            submitBtn.disabled = true;
            
            // Add progress indication
            showProgressIndicator();

            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    displayResults(data);
                } else {
                    showError(data.error || 'Analysis failed');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Network error occurred during analysis');
            })
            .finally(() => {
                // Reset button
                submitBtn.innerHTML = '<i class="fas fa-microscope me-2"></i>Analyze Image';
                submitBtn.disabled = false;
                hideProgressIndicator();
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
            if (!resultsSection) return;

            // Show results section
            resultsSection.classList.remove('d-none');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

            // Display results in the analysisResults div
            const analysisResults = document.getElementById('analysisResults');
            if (analysisResults) {
                let resultsHTML = `
                    <div class="alert alert-success">
                        <h5 class="alert-heading fw-bold"><i class="fas fa-check-circle me-2"></i>Analysis Complete</h5>
                        <p class="mb-0">Medical image analysis has been completed successfully.</p>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card border-primary">
                                <div class="card-header bg-primary text-white">
                                    <h6 class="mb-0"><i class="fas fa-image me-2"></i>Image Information</h6>
                                </div>
                                <div class="card-body">
                                    <p><strong>Status:</strong> <span class="text-success">Processed Successfully</span></p>
                                    <p><strong>Analysis Time:</strong> ${new Date().toLocaleTimeString()}</p>
                                    <p><strong>Image Quality:</strong> <span class="text-success">Good</span></p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card border-info">
                                <div class="card-header bg-info text-white">
                                    <h6 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Analysis Summary</h6>
                                </div>
                                <div class="card-body">
                                    <p><strong>Processing:</strong> <span class="text-success">Complete</span></p>
                                    <p><strong>Confidence:</strong> <span class="text-warning">Pending AI Integration</span></p>
                                    <p><strong>Next Steps:</strong> Review results with medical professional</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="alert alert-info mt-3">
                        <h6 class="alert-heading"><i class="fas fa-info-circle me-2"></i>Note</h6>
                        <p class="mb-0">This is a placeholder for AI analysis results. The actual AI model integration will provide detailed diagnostic insights, confidence scores, and clinical recommendations.</p>
                    </div>
                `;
                
                analysisResults.innerHTML = resultsHTML;
            }
        }

        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-3';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
            
            // Remove any existing error messages
            const existingError = uploadForm.querySelector('.alert-danger');
            if (existingError) {
                existingError.remove();
            }
            
            uploadForm.appendChild(errorDiv);
            
            // Auto-remove error after 5 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 5000);
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
            btn.addEventListener('click', function() {
                if (validateCurrentStep()) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });

        prevBtns.forEach(btn => {
            btn.addEventListener('click', function() {
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

        // Password validation
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