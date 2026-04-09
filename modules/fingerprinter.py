import requests
from core.plugin_base import IntelligenceModule # type: ignore

class Fingerprinter(IntelligenceModule):
    @property
    def name(self) -> str:
        return "Service Fingerprinter"

    def run(self, asset: dict) -> dict:
        ip = asset.get('ip')
        port = asset.get('port')
        findings = {
            "module": self.name, 
            "software": "Unknown", 
            "issues": [], 
            "risk_delta": 0.0
        }

        # Only fingerprint web-capable ports
        if port not in [80, 443, 8080, 8443]:
            return findings

        protocol = "https" if port in [443, 8443] else "http"
        try:
            # HEAD request to get headers only (fast and quiet)
            response = requests.head(f"{protocol}://{ip}:{port}", timeout=2, verify=False)
            
            server = response.headers.get("Server")
            powered_by = response.headers.get("X-Powered-By")

            if server:
                findings["software"] = server
                # Flagging version disclosure as a low-risk config issue
                if any(char.isdigit() for char in server):
                    findings["issues"].append(f"Detailed Server Header: {server}")
                    findings["risk_delta"] += 0.5
            
            if powered_by:
                findings["issues"].append(f"X-Powered-By Disclosure: {powered_by}")
                findings["risk_delta"] += 0.5

        except Exception:
            pass

        return findings