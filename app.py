# app.py
import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
import shutil
import subprocess

UPLOAD_FOLDER = 'uploads'
SOURCE_DIR = os.path.join(UPLOAD_FOLDER, 'Source')
TARGET_DIR = os.path.join(UPLOAD_FOLDER, 'Target')
PREPROCESSED_DIR = 'Preprocessed'
POSTPROCESSED_DIR = 'PostProcessed'

app = Flask(__name__)
app.secret_key = 'localization_secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

for folder in [SOURCE_DIR, TARGET_DIR, PREPROCESSED_DIR, POSTPROCESSED_DIR]:
    os.makedirs(folder, exist_ok=True)

def clear_dirs():
    for folder in [SOURCE_DIR, TARGET_DIR, PREPROCESSED_DIR, POSTPROCESSED_DIR]:
        shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preprocess', methods=['POST'])
def preprocess():
    clear_dirs()
    files = request.files.getlist('source_files')
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(SOURCE_DIR, filename))
    subprocess.run(['python', 'preprocess.py'])
    return redirect(url_for('download_preprocessed'))

@app.route('/postprocess', methods=['POST'])
def postprocess():
    clear_dirs()
    files = request.files.getlist('xliff_files')
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(TARGET_DIR, filename))
    subprocess.run(['python', 'postprocess.py'])
    return redirect(url_for('download_postprocessed'))

@app.route('/download/preprocessed')
def download_preprocessed():
    files = os.listdir(PREPROCESSED_DIR)
    return render_template('download.html', files=files, folder=PREPROCESSED_DIR)

@app.route('/download/postprocessed')
def download_postprocessed():
    subfolders = [f for f in os.listdir(POSTPROCESSED_DIR) if os.path.isdir(os.path.join(POSTPROCESSED_DIR, f))]
    files = []
    for folder in subfolders:
        files += [os.path.join(folder, f) for f in os.listdir(os.path.join(POSTPROCESSED_DIR, folder))]
    return render_template('download.html', files=files, folder=POSTPROCESSED_DIR)

@app.route('/download/<path:folder>/<filename>')
def download_file(folder, filename):
    return send_from_directory(folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
