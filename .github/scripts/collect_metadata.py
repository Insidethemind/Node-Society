import os
import json
from urllib.parse import quote

output = []

fields = [
    "Title",
    "Description",
    "Houdini Version",
    "Tags",
    "Author",
    "Type",
    "Skill Level",
    "Category",
    "Simulation Type"
]

known_keys = set(fields)

def parse_metadata_file(filepath):
    metadata = {}
    current_key = None
    current_value = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')

            if ':' in line:
                possible_key, possible_value = line.split(':', 1)
                if possible_key.strip() in known_keys:
                    if current_key:
                        metadata[current_key] = ' '.join(current_value).replace('\r', '').strip()
                    current_key = possible_key.strip()
                    current_value = [possible_value.strip()]
                else:
                    if current_key:
                        current_value.append(line.strip())
            else:
                if current_key:
                    current_value.append(line.strip())

        if current_key:
            metadata[current_key] = ' '.join(current_value).replace('\r', '').strip()

    return metadata


for root, _, files in os.walk("."):
    for file in files:
        if file == "metadata.txt":
            metadata_path = os.path.join(root, file)
            entry = {field: "" for field in fields}

            parsed = parse_metadata_file(metadata_path)
            for key in entry:
                entry[key] = parsed.get(key, "")

            type_ = entry["Type"].strip()
            title = entry["Title"].strip()
            title_slug = quote(title)

            if type_ == "Project Files":
                skill = quote(entry["Skill Level"].strip())
                category = quote(entry["Category"].strip())
                path = f"Project Files/{skill}/{category}/{title_slug}"
            elif type_ == "Simulations":
                sim_type = quote(entry["Simulation Type"].strip())
                path = f"Simulations/{sim_type}/{title_slug}"
            else:
                type_slug = quote(type_)
                path = f"{type_slug}/{title_slug}"

            entry["Download"] = f"https://github.com/Insidethemind/Node-Society/tree/main/{path}"

            output.append(entry)

os.makedirs("docs", exist_ok=True)
with open("docs/all_metadata_combined.json", "w", encoding="utf-8") as out_file:
    json.dump(output, out_file, indent=2)

print(f"Combined {len(output)} metadata files into docs/all_metadata_combined.json")
