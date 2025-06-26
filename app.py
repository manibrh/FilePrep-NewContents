import os
import shutil
import tempfile
import zipfile
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from tep_preprocess import run_tep_preprocessing
from tep_postprocess import run_tep_postprocessing
from legacy_preprocess import run_legacy_preprocessing
from legacy_postprocess import run_legacy_postprocessing

app = Flask(__name__)
app.secret_key = 'localization_secret'
TEMP_OUTPUT = "static/processed_files"
os.makedirs(TEMP_OUTPUT, exist_ok=True)

def save_files(files, folder):
    os.makedirs(folder, exist_ok=True)
    for file in files:
        filename = secure_filename(file.filename)
        if not filename:
            continue  # skip if no file was selected
        file.save(os.path.join(folder, filename))

@app.route('/')
def index():
    return render_template('ui.html')

@app.route('/process', methods=['POST'])
def process():
    workflow = request.form.get('workflow')
    process_type = request.form.get('processType')
    files = request.files.getlist('files')

    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, 'Input')
        output_dir = os.path.join(temp_dir, 'Output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        if workflow == 'legacy' and process_type == 'preprocess':
            for file in files:
                filename = secure_filename(file.filename)
                if 'source' in filename.lower():
                    file.save(os.path.join(input_dir, 'source_' + filename))
                elif 'target' in filename.lower():
                    file.save(os.path.join(input_dir, 'target_' + filename))
        else:
            save_files(files, input_dir)

        if workflow == 'tep':
            if process_type == 'preprocess':
                run_tep_preprocessing(input_dir, output_dir)
            else:
                run_tep_postprocessing(input_dir, output_dir)
        else:
            if process_type == 'preprocess':
                run_legacy_preprocessing(input_dir, output_dir)
            else:
                run_legacy_postprocessing(input_dir, output_dir)

        if os.path.exists(TEMP_OUTPUT):
            shutil.rmtree(TEMP_OUTPUT)
        shutil.copytree(output_dir, TEMP_OUTPUT)

        zip_path = os.path.join(TEMP_OUTPUT, "batch.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(TEMP_OUTPUT):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, TEMP_OUTPUT)
                    if not arcname.endswith("batch.zip"):
                        zipf.write(file_path, arcname=arcname)

        output_files = []
        for root, _, files in os.walk(TEMP_OUTPUT):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), TEMP_OUTPUT)
                if not rel_path.endswith("batch.zip"):
                    output_files.append(rel_path.replace("\\", "/"))

        return jsonify({"status": "completed", "files": output_files})

@app.route('/download/<path:filename>')
def download(filename):
    file_path = os.path.join(TEMP_OUTPUT, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
