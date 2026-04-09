import os
import sqlite3

from core.db import Database

class Engine:
    def __init__(self):
        self.db = Database()
        self.providers = {}  # Changed to a dict for better control
        self.modules = []

    def register_provider(self, name, provider_instance):
        self.providers[name] = provider_instance
        print(f"[+] Registered Provider: {name}")

    def run_discovery(self, provider_name, query_or_path):
        """Runs discovery using a specific provider."""
        if provider_name not in self.providers:
            print(f"[!] Provider '{provider_name}' not registered.")
            return []

        provider = self.providers[provider_name]
        assets = provider.fetch(query_or_path)
        
        for asset in assets:
            # We ensure minimum fields exist before DB upsert
            if "ip" in asset and "port" in asset:
                self.db.upsert_asset(asset)
        
        return assets


def reset():
    db_path = 'surfacelens.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # This keeps the schema but wipes the data
        cursor.execute("DELETE FROM assets")
        conn.commit()
        conn.close()
        print("[+] SurfaceLens database cleared successfully.")
    else:
        print("[!] No database found to clear.")


if __name__ == "__main__":
    confirm = input("Are you sure you want to wipe all discovered assets? (y/n): ")
    if confirm.lower() == 'y':
        reset()