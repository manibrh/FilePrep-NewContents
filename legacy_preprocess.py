import os
import json
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_properties(path):
    data = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                data[key.strip()] = value.strip()
    return data

def to_xliff(source_dict, target_dict, source_lang, target_lang, original_filename, output_path):
    xliff = ET.Element('xliff', {'version': '1.2'})
    file_tag = ET.SubElement(xliff, 'file', {
        'source-language': source_lang,
        'target-language': target_lang,
        'datatype': 'plaintext',
        'original': original_filename
    })
    body = ET.SubElement(file_tag, 'body')

    common_keys = sorted(set(source_dict.keys()) & set(target_dict.keys()))
    print(f'   🔑 Common keys: {len(common_keys)}')
    for idx, key in enumerate(common_keys, 1):
        trans_unit = ET.SubElement(body, 'trans-unit', {'id': str(idx), 'resname': key})

        source_tag = ET.SubElement(trans_unit, 'source')
        source_tag.text = source_dict.get(key, '')

        target_tag = ET.SubElement(trans_unit, 'target')
        target_tag.text = target_dict.get(key, '')

    xml_str = ET.tostring(xliff, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print(f"   ✅ XLIFF saved: {output_path}\n")

# === MAIN SCRIPT ===
start_time = time.time()
print("\n🚀 Starting CAT-compliant XLIFF generation (multi-source, multi-target)...\n")

base_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(base_dir, 'Source')
target_base = os.path.join(base_dir, 'Target')

language_folders = [f for f in os.listdir(target_base) if os.path.isdir(os.path.join(target_base, f))]
source_files = [f for f in os.listdir(source_dir) if f.endswith(('.json', '.properties'))]

total = 0

for source_file in source_files:
    source_path = os.path.join(source_dir, source_file)
    source_base = os.path.splitext(source_file)[0]         # e.g. Calendar-en
    source_ext = source_file.split('.')[-1]
    if '-' not in source_base:
        print(f"⚠ Skipping invalid filename (no language code): {source_file}")
        continue

    source_lang = source_base.split('-')[-1]
    source_root = '-'.join(source_base.split('-')[:-1])
    source_data = load_json(source_path) if source_ext == 'json' else load_properties(source_path)

    print(f"\n📘 Source: {source_file} | Language: {source_lang} | Keys: {len(source_data)}")

    for lang in language_folders:
        lang_path = os.path.join(target_base, lang)
        target_files = [f for f in os.listdir(lang_path) if f.endswith(('.json', '.properties'))]
        matching_files = [f for f in target_files if f.startswith(source_root)]

        print(f"📂 [{lang}] Checking {len(matching_files)} files for '{source_root}'")

        for target_file in matching_files:
            target_path = os.path.join(lang_path, target_file)
            target_ext = target_file.split('.')[-1]
            target_data = load_json(target_path) if target_ext == 'json' else load_properties(target_path)

            output_file = target_file.rsplit('.', 1)[0] + '.xliff'
            output_path = os.path.join(base_dir, 'bilingual_xliff', lang, output_file)

            print(f"🔄 Generating XLIFF: {target_file}")
            to_xliff(source_data, target_data, source_lang, lang, target_file, output_path)
            total += 1

elapsed = round(time.time() - start_time, 2)
print(f"\n✅ Completed. Total XLIFF files generated: {total} in {elapsed} seconds.")
