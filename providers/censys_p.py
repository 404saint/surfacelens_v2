import os
import requests
from requests.auth import HTTPBasicAuth

class CensysProvider:
    def __init__(self):
        # Store keys but don't validate yet
        self.api_id = os.getenv("CENSYS_API_ID")
        self.api_secret = os.getenv("CENSYS_API_SECRET")
        self.base_url = "https://search.censys.io/api/v2"

    def fetch(self, query: str):
        if not self.api_id or not self.api_secret:
            print(f"\n[!] Censys Skip: CENSYS_API_ID/SECRET not set.")
            return []

        print(f"[*] Querying Censys: {query}")
        url = f"{self.base_url}/hosts/search?q={query}"
        
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self.api_id, self.api_secret))
            response.raise_for_status()
            data = response.json()
            
            assets = []
            for hit in data.get("result", {}).get("hits", []):
                for service in hit.get("services", []):
                    assets.append({
                        "ip": hit.get("ip"),
                        "port": service.get("port"),
                        "service": service.get("service_name"),
                        "banner": "", 
                        "hostnames": hit.get("names", []),
                        "asn": hit.get("autonomous_system", {}).get("asn"),
                        "org": hit.get("autonomous_system", {}).get("name"),
                        "location": hit.get("location", {}),
                        "timestamp": hit.get("last_updated_at")
                    })
            return assets
        except Exception as e:
            print(f"[!] Censys Error: {e}")
            return []