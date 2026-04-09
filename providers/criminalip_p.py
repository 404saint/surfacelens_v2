import os
import requests

class CriminalIPProvider:
    def __init__(self):
        self.api_key = os.getenv("CRIMINALIP_API_KEY")
        self.base_url = "https://api.criminalip.io/v1"

    def fetch(self, query: str):
        if not self.api_key:
            print(f"\n[!] Criminal IP Skip: CRIMINALIP_API_KEY not set.")
            return []

        print(f"[*] Querying Criminal IP: {query}")
        url = f"{self.base_url}/asset/search?query={query}"
        headers = {"x-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            assets = []
            for match in data.get("matches", []):
                assets.append({
                    "ip": match.get("ip_address"),
                    "port": match.get("port"),
                    "service": match.get("product"),
                    "banner": match.get("banner", ""),
                    "hostnames": match.get("hostname", []),
                    "asn": match.get("asn"),
                    "org": match.get("org_name"),
                    "location": {"country": match.get("country_code")},
                    "timestamp": None 
                })
            return assets
        except Exception as e:
            print(f"[!] Criminal IP Error: {e}")
            return []