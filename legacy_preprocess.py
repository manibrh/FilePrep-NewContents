import os
import json
import xml.etree.ElementTree as ET

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_properties(path):
    data = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                data[k.strip()] = v.strip()
    return data

def write_xliff(data, input_file, output_file, src_lang='en', tgt_lang='xx'):
    xliff = ET.Element('xliff', {'version': '1.2'})
    file_tag = ET.SubElement(xliff, 'file', {
        'source-language': src_lang,
        'target-language': tgt_lang,
        'datatype': 'plaintext',
        'original': os.path.basename(input_file)
    })
    body = ET.SubElement(file_tag, 'body')
    for i, (key, val) in enumerate(data.items(), start=1):
        tu = ET.SubElement(body, 'trans-unit', {'id': str(i), 'resname': key})
        ET.SubElement(tu, 'source').text = val

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    ET.ElementTree(xliff).write(output_file, encoding='utf-8', xml_declaration=True)

def run_legacy_preprocessing(input_dir, output_dir):
    # Load source files
    source_files = {
        f.replace("source_", ""): os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.startswith("source_")
    }

    targets_root = os.path.join(input_dir, "targets")
    if not os.path.exists(targets_root):
        raise Exception("Target ZIP not extracted or missing.")

    for lang_code in os.listdir(targets_root):
        lang_folder = os.path.join(targets_root, lang_code)
        if not os.path.isdir(lang_folder):
            continue

        for target_file in os.listdir(lang_folder):
            base_name = os.path.basename(target_file)
            if base_name not in source_files:
                continue  # no matching source

            source_path = source_files[base_name]
            target_path = os.path.join(lang_folder, target_file)

            ext = os.path.splitext(base_name)[1].lower()
            if ext == '.json':
                src_data = read_json(source_path)
                tgt_data = read_json(target_path)
            elif ext == '.properties':
                src_data = read_properties(source_path)
                tgt_data = read_properties(target_path)
            else:
                continue

            filtered = {k: v for k, v in src_data.items() if k in tgt_data}
            output_file = os.path.join(output_dir, lang_code, base_name.replace(ext, ".xliff"))
            write_xliff(filtered, target_path, output_file, tgt_lang=lang_code)
