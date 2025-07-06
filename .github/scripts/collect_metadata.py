import os
import json
from pathlib import Path

# Get absolute path to the repo root
repo_root = Path(__file__).resolve().parents[2]
output_dir = repo_root / "docs"
output_dir.mkdir(parents=True, exist_ok=True)

required_fields = [
    "Title", "Description", "Houdini Version", "Tags", "Author",
    "Type", "Skill Level", "Category", "Simulation Type"
]

metadata_index = []

for root, dirs, files in os.walk(repo_root):
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
            entry["Path"] = filepath.replace("\\", "/").replace(str(repo_root), "").lstrip("/")
            metadata_index.append(entry)
        except Exception as e:
            print(f"Failed to parse {filepath}: {e}")

output_path = output_dir / "metadata_index.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(metadata_index, f, indent=2)

print(f"{len(metadata_index)} metadata entries written to {output_path}")
