import os
import json

required_fields = [
    "Title", "Description", "Houdini Version", "Tags", "Author",
    "Type", "Skill Level", "Category", "Simulation Type"
]

metadata_index = []

for root, dirs, files in os.walk("."):
    if "metadata.txt" in files:
        filepath = os.path.join(root, "metadata.txt")
        entry = {field: "" for field in required_fields}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key in entry:
                            entry[key] = value
            entry["Path"] = filepath.replace("\\", "/")
            metadata_index.append(entry)
        except Exception as e:
            print(f"Failed to parse {filepath}: {e}")

with open("metadata_index.json", "w", encoding="utf-8") as f:
    json.dump(metadata_index, f, indent=2)

print(f"{len(metadata_index)} metadata entries written to metadata_index.json")
