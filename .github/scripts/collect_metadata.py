import os
import json

def collect_metadata(base_path="."):
    metadata_entries = []

    for root, dirs, files in os.walk(base_path):
        if "metadata.txt" in files:
            metadata_path = os.path.join(root, "metadata.txt")
            with open(metadata_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            entry = {"path": os.path.relpath(root, base_path)}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    entry[key.strip()] = value.strip()
            metadata_entries.append(entry)

    return metadata_entries

if __name__ == "__main__":
    base_path = "."
    output_path = "metadata_index.json"

    metadata = collect_metadata(base_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"{len(metadata)} metadata entries written to {output_path}")
