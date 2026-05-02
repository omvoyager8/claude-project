from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

from pipeline_runner import process_hyperspectral
from s3_utils import upload_to_s3

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

CORS(app)

INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():

    print("==== /detect endpoint called ====")

    # Check if request contains file
    if 'file' not in request.files:
        print("Error: No file key in request")
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']

    # Check if filename exists
    if file.filename == "":
        print("Error: Empty filename")
        return jsonify({"error": "No file selected"}), 400

    print("File received:", file.filename)

    try:
        # Save uploaded file
        file_path = os.path.join(INPUT_DIR, file.filename)
        file.save(file_path)

        print("File saved at:", file_path)

        # Optional: Upload to S3
        try:
            upload_to_s3(file_path, f"inputs/{file.filename}")
            print("Uploaded to S3")
        except Exception as e:
            print("S3 upload skipped:", e)

        # Run ML pipeline
        print("Starting anomaly detection pipeline...")
        result_path = process_hyperspectral(file_path)

        print("Pipeline completed successfully")

        return jsonify({
            "status": "success",
            "result_image": f"/static/anomaly_image/{os.path.basename(result_path)}"
        })

    except Exception as e:
        print("Pipeline error:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)