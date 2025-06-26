import os
import json
import xml.etree.ElementTree as ET

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_properties(file_path):
    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                data[key.strip()] = val.strip()
    return data

def write_xliff(data, input_file, output_file, src_lang='en', tgt_lang='fr'):
    xliff = ET.Element('xliff', {'version': '1.2'})
    file_tag = ET.SubElement(xliff, 'file', {
        'source-language': src_lang,
        'target-language': tgt_lang,
        'datatype': 'plaintext',
        'original': os.path.basename(input_file)
    })
    body = ET.SubElement(file_tag, 'body')

    for i, (key, value) in enumerate(data.items(), start=1):
        tu = ET.SubElement(body, 'trans-unit', {'id': str(i), 'resname': key})
        ET.SubElement(tu, 'source').text = value

    tree = ET.ElementTree(xliff)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

def run_legacy_preprocessing(input_dir, output_dir):
    source_file = None
    target_file = None

    for f in os.listdir(input_dir):
        if 'source' in f.lower():
            source_file = os.path.join(input_dir, f)
        elif 'target' in f.lower():
            target_file = os.path.join(input_dir, f)

    if not source_file or not target_file:
        raise FileNotFoundError("Both source and target files must be uploaded.")

    source_ext = os.path.splitext(source_file)[1].lower()
    if source_ext == '.json':
        source_data = read_json(source_file)
        target_data = read_json(target_file)
    elif source_ext == '.properties':
        source_data = read_properties(source_file)
        target_data = read_properties(target_file)
    else:
        raise ValueError("Unsupported file format")

    filtered_data = {k: v for k, v in source_data.items() if k in target_data}
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(target_file))[0] + '.xliff')
    write_xliff(filtered_data, target_file, output_file)
