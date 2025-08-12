from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from functools import wraps
from werkzeug.utils import secure_filename

# Allowed file extensions for medical images
allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

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

@app.route('/home')
def home():
    # Main diagnostic interface for X-ray upload
    return render_template("home.html")

@app.route("/process", methods=["POST"])
def upload_xray():
    """
    Handle uploaded chest X-ray images (UI only - no AI processing)
    """
    # Check if the 'xray' key exists in the request.files dictionary
    if 'xray' not in request.files:
        return jsonify({'error': 'No X-ray image uploaded', 'status': 'error'})

    # Retrieve the file object from the request
    file = request.files['xray']
    
    # Check if the filename is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected', 'status': 'error'})

    # Extract additional form data
    patient_id = request.form.get('patientId', '')
    patient_age = request.form.get('patientAge', '')
    clinical_notes = request.form.get('clinicalNotes', '')

    # Validate file extension
    filename = secure_filename(file.filename).lower()
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file format. Please upload PNG, JPEG, BMP, or TIFF files only.', 'status': 'error'})

    try:
        # Simulate successful upload
        response_data = {
            'status': 'success',
            'message': 'X-ray uploaded successfully!',
            'patient_id': patient_id,
            'patient_age': patient_age,
            'clinical_notes': clinical_notes,
            'filename': filename,
            'file_size': len(file.read()),
            'note': 'This is a demonstration. In a real medical setting, this would connect to AI diagnostic systems.'
        }

        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"Error processing X-ray upload: {str(e)}")
        return jsonify({'error': 'Internal server error during upload', 'status': 'error'})

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
