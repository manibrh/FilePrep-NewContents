# app.py
import os
import shutil
import tempfile
import zipfile
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from preprocess import run_preprocessing
from postprocess import run_postprocessing

app = Flask(__name__)
app.secret_key = 'localization_secret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preprocess', methods=['POST'])
def preprocess():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "Source")
        output_dir = os.path.join(temp_dir, "Preprocessed")
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        files = request.files.getlist('source_files')
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(source_dir, filename))

        run_preprocessing(source_dir, output_dir)

        zip_path = os.path.join(temp_dir, "preprocessed_output.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, output_dir))

        return send_file(zip_path, as_attachment=True)

@app.route('/postprocess', methods=['POST'])
def postprocess():
    with tempfile.TemporaryDirectory() as temp_dir:
        xliff_dir = os.path.join(temp_dir, "Target")
        output_dir = os.path.join(temp_dir, "PostProcessed")
        os.makedirs(xliff_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        files = request.files.getlist('xliff_files')
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(xliff_dir, filename))

        run_postprocessing(xliff_dir, output_dir)

        zip_path = os.path.join(temp_dir, "postprocessed_output.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, output_dir))

        return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
