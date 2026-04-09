import shodan
import os

class ShodanProvider:
    def __init__(self):
        # We store the key, but we don't initialize the client yet
        # to avoid crashing if the key is missing during registration.
        self.api_key = os.getenv("SHODAN_API_KEY")

    def fetch(self, query: str):
        if not self.api_key:
            print(f"\n[!] Shodan Skip: SHODAN_API_KEY environment variable not set.")
            return []
        
        print(f"[*] Querying Shodan: {query}")
        try:
            client = shodan.Shodan(self.api_key)
            results = client.search(query)
            assets = []
            for match in results.get("matches", []):
                assets.append({
                    "ip": match.get("ip_str"),
                    "port": match.get("port"),
                    "service": match.get("product", "unknown"),
                    "banner": match.get("data", ""),
                    "hostnames": match.get("hostnames", []),
                    "asn": match.get("asn"),
                    "org": match.get("org"),
                    "location": match.get("location", {}),
                    "timestamp": match.get("timestamp")
                })
            return assets
        except Exception as e:
            print(f"[!] Shodan API Error: {e}")
            return []