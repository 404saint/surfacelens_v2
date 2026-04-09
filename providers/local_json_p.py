import json
import os

class LocalJSONProvider:
    def __init__(self):
        self.name = "LocalJSON"

    def fetch(self, file_path: str):
        """
        Reads a JSON file and returns a list of assets.
        Expects the V1/V2 standard asset format.
        """
        print(f"[*] Importing from local file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[!] File not found: {file_path}")
            return []

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # In V1, the data was sometimes inside a 'matches' key or a list
            assets = data if isinstance(data, list) else data.get("assets", [])
            
            print(f"[+] Successfully loaded {len(assets)} assets from local storage.")
            return assets
        except Exception as e:
            print(f"[!] Failed to parse local JSON: {e}")
            return []