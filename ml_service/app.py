import os
from flask import Flask, request, jsonify, send_file
from scripts.gradcam_backend import process_image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
GRADCAM_FOLDER = "gradcams"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRADCAM_FOLDER, exist_ok=True)

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    img_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(img_path)

    pred_label, gradcam_path = process_image(img_path)

    return jsonify({
        "prediction": pred_label,
        "gradcam_image_url": f"/gradcam/{os.path.basename(gradcam_path)}"
    })

@app.route("/gradcam/<filename>")
def serve_gradcam(filename):
    return send_file(os.path.join(GRADCAM_FOLDER, filename), mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
