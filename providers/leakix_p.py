import requests
import os
import colorama
from colorama import Fore, Style, init

class LeakIXProvider:
    def __init__(self):
        # Grab key from env if it exists, otherwise stay None
        self.api_key = os.getenv("LEAKIX_API_KEY")

    def fetch(self, query: str):
        print(f"[*] Querying LeakIX: {query}")
        
        # Using the /search endpoint with 'service' scope is often more stable
        url = f"https://leakix.net/search?scope=service&q={query}"
        headers = {'Accept': 'application/json'}
        if self.api_key:
            headers['api-key'] = self.api_key
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 401:
                print(f"{Fore.RED}[!] LeakIX requires an API key for this query.") # type: ignore
                return []
            
            response.raise_for_status()
            results = response.json()
            
            assets = []
            for hit in results:
                assets.append({
                    "ip": hit.get("ip"),
                    "port": hit.get("port"),
                    "service": hit.get("protocol"),
                    "banner": hit.get("summary", ""),
                    "hostnames": [hit.get("hostname")] if hit.get("hostname") else [],
                    "timestamp": hit.get("time")
                })
            return assets
        except Exception as e:
            print(f"[!] LeakIX Error: {e}")
            return []