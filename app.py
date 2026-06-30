from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os

from Backend.pipeline_runner import process_hyperspectral
from Backend.s3_utils import upload_to_s3
from Backend.report_generator import generate_report

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
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
        result_path, stats = process_hyperspectral(file_path)

        # Generate PDF report
        report_path = generate_report(file.filename, stats, result_path)

        print("Pipeline completed successfully")

        return jsonify({
            "status": "success",
            "result_image": f"/static/output/{os.path.basename(result_path)}",
            "report_url": "/report"
        })

    except Exception as e:
        print("Pipeline error:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/report")
def download_report():
    report_path = os.path.abspath("static/output/anomaly_report.pdf")
    if not os.path.exists(report_path):
        return jsonify({"error": "No report generated yet. Run detection first."}), 404
    return send_file(report_path, as_attachment=True, download_name="anomaly_report.pdf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)