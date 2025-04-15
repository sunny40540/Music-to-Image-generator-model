from flask import Flask, request, render_template, send_file
import os
from newproj import extract_metadata, get_wikipedia_info, generate_image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if not file:
        return "No file uploaded", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    metadata, error = extract_metadata(filepath)
    if error:
        return f"<h3>{error}</h3>"

    if metadata["year"] == "Unknown":
        return "<h3>Year not found in metadata.</h3>"

    era_info = get_wikipedia_info(metadata["year"])
    image_path = generate_image(metadata, era_info)

    return render_template("result.html", metadata=metadata, era_info=era_info, image_path=image_path)

@app.route("/image/<filename>")
def serve_image(filename):
    return send_file(os.path.join(".", filename), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
