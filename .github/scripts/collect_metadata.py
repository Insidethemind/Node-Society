import os
import json

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

for root, _, files in os.walk("."):
    for file in files:
        if file == "metadata.txt":
            entry = {field: "" for field in fields}
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in entry:
                            entry[key] = value
            output.append(entry)

os.makedirs("combined", exist_ok=True)
with open("combined/all_metadata_combined.json", "w", encoding="utf-8") as out_file:
    json.dump(output, out_file, indent=2)
