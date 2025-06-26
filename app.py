from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
import shutil
from preprocess import process_folder as preprocess_files
from postprocess import process_xliffs as postprocess_files

app = Flask(__name__)
app.secret_key = "localization_secret"

UPLOAD_SOURCE = "Source"
UPLOAD_TARGET = "Target"
PREPROCESSED = "Preprocessed"
POSTPROCESSED = "PostProcessed"

# Ensure all dirs exist
for folder in [UPLOAD_SOURCE, UPLOAD_TARGET, PREPROCESSED, POSTPROCESSED]:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_source', methods=['POST'])
def upload_source():
    files = request.files.getlist('source_files')
    for file in files:
        if file.filename.endswith(('.json', '.properties')):
            file.save(os.path.join(UPLOAD_SOURCE, file.filename))
    preprocess_files()
    flash("✅ Preprocessing complete.")
    return redirect(url_for('index'))

@app.route('/upload_target', methods=['POST'])
def upload_target():
    files = request.files.getlist('target_files')
    for file in files:
        if file.filename.endswith('.xliff'):
            file.save(os.path.join(UPLOAD_TARGET, file.filename))
    postprocess_files()
    flash("✅ Postprocessing complete.")
    return redirect(url_for('index'))

@app.route('/downloads/<folder>/<path:filename>')
def download_file(folder, filename):
    return send_from_directory(folder, filename, as_attachment=True)

@app.route('/list_files/<folder>')
def list_files(folder):
    path = folder
    files = os.listdir(path)
    return {"files": files}

if __name__ == "__main__":
    app.run(debug=True)
