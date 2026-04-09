import socket
from core.plugin_base import IntelligenceModule # type: ignore

class DNSCorrelator(IntelligenceModule):
    @property
    def name(self) -> str:
        return "DNS Correlator"

    def run(self, asset: dict, target_domain: str = None) -> dict:
        """
        Performs reverse DNS lookups and checks for domain affiliation.
        """
        ip = asset.get('ip')
        findings = {
            "module": self.name, 
            "reverse_dns": None, 
            "is_affiliated": False, 
            "risk_delta": 0.0
        }

        if not ip:
            return findings

        try:
            # Perform Reverse DNS lookup
            reverse_host = socket.gethostbyaddr(ip)[0]
            findings["reverse_dns"] = reverse_host

            # High-signal logic: Check for Shadow IT / Affiliation
            if target_domain:
                if target_domain.lower() in reverse_host.lower():
                    findings["is_affiliated"] = True
                else:
                    # If it's a known asset but the DNS doesn't match the corporate domain
                    # it might be an orphaned or shadow asset.
                    findings["issues"] = ["Reverse DNS mismatch with target domain"]
                    findings["risk_delta"] = 1.5
                    
        except (socket.herror, socket.gaierror):
            findings["reverse_dns"] = "No PTR record found"
            findings["issues"] = ["Missing Reverse DNS (Common in stealth/shadow assets)"]
            findings["risk_delta"] = 0.5

        return findings