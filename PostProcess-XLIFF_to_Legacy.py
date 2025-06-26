import os
import json
import time
import xml.etree.ElementTree as ET

def extract_translations(xliff_path):
    try:
        tree = ET.parse(xliff_path)
        root = tree.getroot()
        file_tag = root.find('file')
        lang = file_tag.attrib.get('target-language', 'xx-XX')
        original = file_tag.attrib.get('original', f'{lang}.json')
        ext = original.split('.')[-1].lower()
        translations = {}
        for unit in file_tag.find('body').findall('trans-unit'):
            key = unit.attrib.get('resname')
            val = unit.find('target').text or ''
            translations[key] = val
        return translations, lang, original, ext
    except Exception as e:
        print(f"❌ Error parsing XLIFF: {xliff_path}\n   Reason: {e}")
        return None, None, None, None

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_properties(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        for k, v in data.items():
            f.write(f'{k}={v}\n')

# === MAIN SCRIPT ===
start_time = time.time()
print("\n🚀 Starting legacy conversion from XLIFF to localized format...\n")

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, 'Reviewed')
output_dir = os.path.join(base_dir, 'Postprocessed')

lang_folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]
total_files = 0

for lang in lang_folders:
    lang_path = os.path.join(input_dir, lang)
    xliff_files = [f for f in os.listdir(lang_path) if f.endswith('.xliff')]

    print(f"🌐 [{lang}] Processing {len(xliff_files)} XLIFF file(s)")

    for idx, xliff_file in enumerate(xliff_files, 1):
        xliff_path = os.path.join(lang_path, xliff_file)
        print(f"🔄 ({idx}/{len(xliff_files)}) Extracting: {xliff_file}")

        translations, lang_code, original_name, ext = extract_translations(xliff_path)
        if not translations:
            continue

        out_folder = os.path.join(output_dir, lang_code)
        os.makedirs(out_folder, exist_ok=True)
        out_path = os.path.join(out_folder, original_name)

        try:
            if ext == 'json':
                save_json(translations, out_path)
            elif ext == 'properties':
                save_properties(translations, out_path)
            else:
                print(f"⚠ Unknown extension '{ext}' — skipping file: {original_name}")
                continue

            print(f"✅ Localized file saved: {out_path}\n")
            total_files += 1
        except Exception as e:
            print(f"❌ Error writing file {original_name}: {e}")

elapsed = round(time.time() - start_time, 2)
print(f"\n✅ Completed. {total_files} localized files generated in {elapsed} seconds.")
