from flask import render_template, request, redirect, url_for, flash,jsonify
from app import app
from functools import wraps
import PyPDF2

allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    elif request.method=="POST":
        return redirect("/signin")

@app.route('/signin', methods=["GET","POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        # Assuming authentication is successful and user session is set

       # session["user_id"] = user_id  # Set the user session ID
        return redirect(url_for('home'))  # Redirect to the home page

@app.route('/home')
def home():
    # Logic for home page
    return render_template("home.html")
@app.route("/process", methods=["POST"])
# Route for uploading a resume
def upload_resume():
    # Check if the 'file' key exists in the request.files dictionary
    if 'resume' not in request.files:
        # If 'file' key is not found, return an error response
        print(request.files,"1st")
        return jsonify({'error': 'No file part'})

    # Retrieve the file object from the request
    file = request.files['resume']
    print(file)
    print(request.files,"3st")
    try:
        pdf = PyPDF2.PdfFileReader(file)
        if pdf.numPages > 0:
            return jsonify({'message': 'PDF file uploaded'})
    except PyPDF2.utils.PdfReadError:
        return jsonify({'error': 'Unsupported file type'})

      

    # Check if the filename is empty
    if file.filename == '':
        # If filename is empty, return an error response
        return jsonify({'error': 'No selected file'})

    # Extract the lowercase filename
    filename = file.filename.lower()

    # Check if the filename has a valid extension
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        # If the file extension is not valid, return an error response
        return jsonify({'error': 'Invalid file extension'})

    # Handle PDF file
    if filename.endswith('.pdf'):
        # Process the PDF file (replace this with your actual PDF processing code)
        # Here, we are returning a success message indicating that the PDF file was uploaded
        return jsonify({'message': 'PDF file uploaded'})

    # Handle image file
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        # Process the image file (replace this with your actual image processing code)
        # Here, we are returning a success message indicating that the image file was uploaded
        return jsonify({'message': 'Image file uploaded'})

    # Handle Word document
    if filename.endswith(('.doc', '.docx')):
        # Process the Word document (replace this with your actual document processing code)
        # Here, we are returning a success message indicating that the Word document was uploaded
        return jsonify({'message': 'Word document uploaded'})

    # If the file type is not recognized, return an error response
    return jsonify({'error': 'Unsupported file type'})
