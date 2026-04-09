import requests
from core.plugin_base import IntelligenceModule # type: ignore

class Hunter(IntelligenceModule):
    @property
    def name(self) -> str:
        return "Sensitive File Hunter"

    def run(self, asset: dict) -> dict:
        ip = asset.get('ip')
        port = asset.get('port')
        findings = {"module": self.name, "discovered_files": [], "risk_delta": 0.0, "issues": []}

        # Only hunt on web ports
        if port not in [80, 443, 8080, 8443]:
            return findings

        protocol = "https" if port in [443, 8443] else "http"
        base_url = f"{protocol}://{ip}:{port}"
        
        # High-value targets
        targets = {
            "/.env": "Environment File Exposed",
            "/.git/config": "Git Source Metadata Exposed",
            "/robots.txt": "Robots.txt Found",
            "/.vscode/sftp.json": "SFTP Credentials Exposed"
        }

        for path, issue in targets.items():
            try:
                # We use a 2-second timeout to keep the tool fast
                response = requests.get(f"{base_url}{path}", timeout=2, verify=False, allow_redirects=False)
                
                if response.status_code == 200:
                    # Double check it's not a generic 'OK' page (soft 404)
                    if len(response.text) > 0:
                        findings["discovered_files"].append(path)
                        findings["issues"].append(issue)
                        
                        # .env and .git are critical hits
                        if ".env" in path or ".git" in path:
                            findings["risk_delta"] += 4.0
                        else:
                            findings["risk_delta"] += 0.5
                            
            except Exception:
                continue

        return findings