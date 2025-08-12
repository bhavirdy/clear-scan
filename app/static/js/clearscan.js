document.addEventListener('DOMContentLoaded', function() {
    // ClearScan X-ray Upload and Analysis Functionality
    const uploadForm = document.getElementById('uploadForm');
    const xrayInput = document.getElementById('xray');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const resultsSection = document.getElementById('resultsSection');
    
    if (uploadForm && xrayInput && fileNameDisplay) {
        // Drag and drop functionality
        const dropzone = document.querySelector('.dropzone-inner');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropzone.classList.add('bg-light');
        }

        function unhighlight() {
            dropzone.classList.remove('bg-light');
        }

        dropzone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                xrayInput.files = files;
                handleFileSelection(files[0]);
            }
        }

        // File input change handler
        xrayInput.addEventListener('change', function(event) {
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

            // Display file name
            fileNameDisplay.innerHTML = `<i class="fas fa-check-circle me-2"></i>Selected: ${file.name}`;
            
            // Show file size
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            fileNameDisplay.innerHTML += `<br><small class="text-muted">Size: ${fileSize} MB</small>`;
        }

        // Form submission handler
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            if (!xrayInput.files || xrayInput.files.length === 0) {
                alert('Please select an X-ray image first');
                return;
            }

            analyzeXray();
        });

        function analyzeXray() {
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
                submitBtn.innerHTML = '<i class="fas fa-stethoscope me-2"></i>Analyze X-ray';
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
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });

            // Display original image preview (mock implementation)
            const originalImageDiv = document.getElementById('originalImage');
            if (originalImageDiv) {
                originalImageDiv.innerHTML = '<div class="text-center text-muted p-4"><i class="fas fa-image fa-3x mb-2"></i><br>Original X-ray Image</div>';
            }

            // Display heatmap if available
            const heatmapImageDiv = document.getElementById('heatmapImage');
            if (heatmapImageDiv) {
                if (data.heatmap) {
                    heatmapImageDiv.innerHTML = `<img src="${data.heatmap}" class="img-fluid rounded" alt="Grad-CAM Heatmap">`;
                } else {
                    heatmapImageDiv.innerHTML = '<div class="text-center text-muted p-4"><i class="fas fa-map-marked-alt fa-3x mb-2"></i><br>Heatmap not generated</div>';
                }
            }

            // Display predictions
            const predictionsDiv = document.getElementById('predictions');
            if (predictionsDiv && data.predictions) {
                let predictionsHTML = '<div class="row">';
                
                Object.entries(data.predictions).forEach(([condition, probability]) => {
                    const percentage = (probability * 100).toFixed(1);
                    const confidenceClass = percentage > 70 ? 'confidence-high' : 
                                          percentage > 40 ? 'confidence-medium' : 'confidence-low';
                    
                    predictionsHTML += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6 class="card-title">${condition.charAt(0).toUpperCase() + condition.slice(1)}</h6>
                                    <div class="progress mb-2">
                                        <div class="progress-bar ${confidenceClass === 'confidence-high' ? 'bg-success' : 
                                                                   confidenceClass === 'confidence-medium' ? 'bg-warning' : 'bg-danger'}" 
                                             style="width: ${percentage}%"></div>
                                    </div>
                                    <span class="${confidenceClass}">${percentage}%</span>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                predictionsHTML += '</div>';
                
                // Add primary diagnosis summary
                predictionsHTML += `
                    <div class="alert alert-info mt-3">
                        <h5><i class="fas fa-diagnoses me-2"></i>Primary Diagnosis</h5>
                        <p><strong>${data.primary_diagnosis}</strong> (Confidence: ${data.confidence_level})</p>
                        <p>${data.explanation}</p>
                    </div>
                `;
                
                // Add recommendations
                if (data.recommendations && data.recommendations.length > 0) {
                    predictionsHTML += '<div class="alert alert-warning mt-3"><h6><i class="fas fa-lightbulb me-2"></i>Clinical Recommendations</h6><ul>';
                    data.recommendations.forEach(rec => {
                        predictionsHTML += `<li>${rec}</li>`;
                    });
                    predictionsHTML += '</ul></div>';
                }
                
                predictionsDiv.innerHTML = predictionsHTML;
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