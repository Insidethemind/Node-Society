import os
import json

output = []

# Define the expected keys in each metadata file
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

# Walk through all folders in the repo looking for metadata.txt files
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
            output.append(entry)

# Ensure the output directory exists
os.makedirs("docs", exist_ok=True)

# Write out the combined metadata as JSON
with open("docs/all_metadata_combined.json", "w", encoding="utf-8") as out_file:
    json.dump(output, out_file, indent=2)

print(f"Combined {len(output)} metadata files into combined/all_metadata_combined.json")
