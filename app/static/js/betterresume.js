document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const resumeInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    if (uploadForm && resumeInput && fileNameDisplay) {
        uploadForm.addEventListener('dragover', function(event) {
            event.preventDefault();
            uploadForm.classList.add('dragover');
        });

        uploadForm.addEventListener('dragleave', function(event) {
            event.preventDefault();
            uploadForm.classList.remove('dragover');
        });

        uploadForm.addEventListener('drop', function(event) {
            event.preventDefault();
            uploadForm.classList.remove('dragover');
            const file = event.dataTransfer.files[0];
            handleFileUpload(file);
        });

        resumeInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            handleFileUpload(file);
        });

        function handleFileUpload(file) {
            fileNameDisplay.textContent = file.name;
        }
    }

    if (nextBtn && prevBtn && submitBtn) {
        const step1 = document.getElementById('step1');
        const step2 = document.getElementById('step2');
        const step3 = document.getElementById('step3');
        const step4 = document.getElementById('step4');
        const step5 = document.getElementById('step5');
        const step6 = document.getElementById('step6');
        const step7 = document.getElementById('step7');

        let currentStep = 1; // Start from Step 1

        function showStep(stepIndex) {
            step1.style.display = stepIndex === 1 ? 'block' : 'none';
            step2.style.display = stepIndex === 2 ? 'block' : 'none';
            step3.style.display = stepIndex === 3 ? 'block' : 'none';
            step4.style.display = stepIndex === 4 ? 'block' : 'none';
            step5.style.display = stepIndex === 5 ? 'block' : 'none';
            step6.style.display = stepIndex === 6 ? 'block' : 'none';
            step7.style.display = stepIndex === 7 ? 'block' : 'none';

            prevBtn.style.display = stepIndex === 1 ? 'none' : 'block';
            nextBtn.style.display = stepIndex === 7 ? 'none' : 'block';
            submitBtn.style.display = stepIndex === 7 ? 'block' : 'none';
        }

        function validateNames() {
            const firstName = document.getElementById('inputFirstName').value.trim();
            const lastName = document.getElementById('inputLastName').value.trim();
            const nameError = document.getElementById('nameError');
            if (firstName === '' || lastName === '') {
                nameError.textContent = 'Please enter valid first name and last name.';
                return false;
            } else {
                nameError.textContent = '';
                return true;
            }
        }

        function validatePhone() {
            const phone = document.getElementById('inputPhone').value.trim();
            const phonePattern = /^\d{10}$/; // Change this to the desired phone number pattern
            const phoneError = document.getElementById('phoneError');
            if (!phonePattern.test(phone)) {
                phoneError.textContent = 'Please enter a valid phone number.';
                return false;
            } else {
                phoneError.textContent = '';
                return true;
            }
        }

        nextBtn.addEventListener('click', function() {
            if (currentStep === 1) {
                if (!validateNames()) return;
            } else if (currentStep === 2) {
                if (!validatePhone()) return;
            }
            currentStep++;
            showStep(currentStep);
        });

        prevBtn.addEventListener('click', function() {
            currentStep--;
            showStep(currentStep);
        });

        showStep(currentStep);
    }
});










