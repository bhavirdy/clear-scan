import os
from flask import Flask, render_template, request, jsonify, send_file
from scripts.gradcam_backend import process_image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
GRADCAM_FOLDER = "gradcams"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRADCAM_FOLDER, exist_ok=True)

@app.route("/home", methods=["GET", "POST"])
def home():
    # Render the home page with Patient Info hidden
    return render_template("home.html", show_patient_info=False)


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    img_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(img_path)

    try:
        pred_label, confidence, gradcam_path = process_image(img_path)

        return jsonify({
            "prediction": pred_label,
            "confidence": confidence,
            "gradcam_image_url": f"/gradcam/{os.path.basename(gradcam_path)}"
        })
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/gradcam/<filename>")
def serve_gradcam(filename):
    return send_file(os.path.join(GRADCAM_FOLDER, filename), mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
