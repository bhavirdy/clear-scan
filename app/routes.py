from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from functools import wraps
from werkzeug.utils import secure_filename
import requests
import os

# Allowed file extensions for medical images
allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

# ML Service configuration - support for containerized deployment
ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://localhost:5002')

@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration"""
    return jsonify({
        'status': 'healthy',
        'service': 'frontend',
        'ml_service_url': ML_SERVICE_URL
    }), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        # Handle healthcare professional registration
        # Extract form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        specialty = request.form.get('specialty')
        institution = request.form.get('institution')
        registration = request.form.get('registration')
        password = request.form.get('password')
        
        # TODO: Implement user registration logic
        # - Validate medical registration number
        # - Hash password
        # - Store user in database
        # - Send verification email
        
        flash('Registration successful! Please check your email for verification.', 'success')
        return redirect("/signin")

@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        # TODO: Implement authentication logic
        # - Validate credentials
        # - Check medical license status
        # - Create session
        
        # Assuming authentication is successful and user session is set
        # session["user_id"] = user_id  # Set the user session ID
        return redirect(url_for('home'))  # Redirect to the diagnostic home page

@app.route("/home", methods=["GET", "POST"])
def home():
    # Main diagnostic interface for X-ray upload
    # Patient Info section is hidden
    return render_template("home.html", show_patient_info=False)


@app.route("/process", methods=["POST"])
def upload_xray():
    """
    Handle uploaded medical images and send to ML service for analysis
    """
    # Check if the 'file' key exists in the request.files dictionary
    if 'file' not in request.files:
        return jsonify({'error': 'No medical image uploaded', 'status': 'error'})

    # Retrieve the file object from the request
    file = request.files['file']
    
    # Check if the filename is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected', 'status': 'error'})

    # Extract additional form data
    patient_id = request.form.get('patient_id', '')
    patient_age = request.form.get('patient_age', '')
    patient_gender = request.form.get('patient_gender', '')
    study_type = request.form.get('study_type', '')
    clinical_notes = request.form.get('clinical_notes', '')

    # Validate file extension
    filename = secure_filename(file.filename).lower()
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file format. Please upload PNG, JPEG, BMP, or TIFF files only.', 'status': 'error'})

    try:
        # Prepare file for ML service
        file.seek(0)  # Reset file pointer
        files = {'file': (file.filename, file.stream, file.content_type)}
        
        # Send file to ML service
        ml_response = requests.post(f'{ML_SERVICE_URL}/predict', files=files, timeout=30)
        
        if ml_response.status_code == 200:
            ml_data = ml_response.json()
            
            # Successful ML analysis
            response_data = {
                'status': 'success',
                'message': 'Medical image analyzed successfully!',
                'patient_id': patient_id,
                'patient_age': patient_age,
                'patient_gender': patient_gender,
                'study_type': study_type,
                'clinical_notes': clinical_notes,
                'filename': filename,
                'prediction': ml_data.get('prediction', 'No prediction available'),
                'confidence': ml_data.get('confidence', 0),
                'gradcam_image_url': ml_data.get('gradcam_image_url', ''),
                'ml_service_response': ml_data
            }
            
            return jsonify(response_data)
            
        else:
            # ML service error
            app.logger.error(f"ML service returned status {ml_response.status_code}: {ml_response.text}")
            return jsonify({
                'error': f'ML service error: {ml_response.status_code}',
                'status': 'error',
                'fallback_message': 'Analysis service temporarily unavailable'
            })

    except requests.exceptions.ConnectionError:
        app.logger.error("Could not connect to ML service")
        return jsonify({
            'error': 'Could not connect to ML analysis service',
            'status': 'error',
            'fallback_message': 'Please ensure the ML service is running on port 5000'
        })
    except requests.exceptions.Timeout:
        app.logger.error("ML service request timed out")
        return jsonify({
            'error': 'Analysis request timed out',
            'status': 'error',
            'fallback_message': 'Image analysis is taking longer than expected'
        })
    except Exception as e:
        app.logger.error(f"Error processing medical image: {str(e)}")
        return jsonify({
            'error': 'Internal server error during analysis',
            'status': 'error',
            'fallback_message': 'An unexpected error occurred'
        })

@app.route('/gradcam/<filename>')
def gradcam_proxy(filename):
    """Proxy gradcam images from ML service"""
    try:
        response = requests.get(f'{ML_SERVICE_URL}/gradcam/{filename}')
        if response.status_code == 200:
            return response.content, 200, {'Content-Type': 'image/png'}
        else:
            return "Image not found", 404
    except Exception as e:
        return f"Error fetching image: {str(e)}", 500

@app.route('/history')
def history():
    """
    Display patient analysis history (UI placeholder)
    """
    return render_template('history.html')

@app.route('/reports')
def reports():
    """
    Generate and download diagnostic reports (UI placeholder)
    """
    return render_template('reports.html')
