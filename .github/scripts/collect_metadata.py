import os
import json
from urllib.parse import quote

output = []

# Expected metadata fields
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

# Traverse all metadata.txt files
for root, _, files in os.walk("."):
    for file in files:
        if file == "metadata.txt":
            metadata_path = os.path.join(root, file)
            entry = {field: "" for field in fields}

            with open(metadata_path, "r", encoding="utf-8") as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in entry:
                            entry[key] = value

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

            # Create full GitHub folder URL
            entry["Download"] = f"https://github.com/Insidethemind/Node-Society/tree/main/{path}"

            output.append(entry)

# Write combined JSON file to /docs
os.makedirs("docs", exist_ok=True)
with open("docs/all_metadata_combined.json", "w", encoding="utf-8") as out_file:
    json.dump(output, out_file, indent=2)

print(f"Combined {len(output)} metadata files into docs/all_metadata_combined.json")
