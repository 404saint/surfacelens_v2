import ssl
import socket
from datetime import datetime
from core.plugin_base import IntelligenceModule # type: ignore

class SSLAuditor(IntelligenceModule):
    @property
    def name(self) -> str:
        return "SSL/TLS Auditor"

    def run(self, asset: dict) -> dict:
        """
        Attempts to pull and analyze the SSL certificate for the given asset.
        """
        ip = asset.get('ip')
        port = asset.get('port')
        findings = {"module": self.name, "issues": [], "risk_delta": 0.0}

        # We only audit typical SSL/TLS ports to save time
        if port not in [443, 8443, 9443, 636, 993, 995]:
            return findings

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE # We want the cert even if it's "bad"

            with socket.create_connection((ip, port), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    # Use a basic parser or cryptography lib for deeper logic
                    # For now, we detect if a cert is even present
                    findings["cert_present"] = True
                    findings["protocol"] = ssock.version()
                    
                    # High-signal logic: Detect old protocols
                    if "TLSv1.1" in findings["protocol"] or "TLSv1.0" in findings["protocol"]:
                        findings["issues"].append("Deprecated TLS Version")
                        findings["risk_delta"] += 2.0
                        
        except Exception as e:
            findings["error"] = str(e)
            findings["cert_present"] = False

        return findings