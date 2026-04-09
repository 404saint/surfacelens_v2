import socket
import colorama
from colorama import Fore, Style, init
class ActiveScanProvider:
    def __init__(self):
        self.common_ports = [80, 443, 8080, 8443, 3389, 445, 21, 22, 23]

    def fetch(self, target_ip: str):
        """
        Performs a quick TCP connect scan on common ports.
        """
        print(f"[*] Actively scanning {target_ip}...")
        assets = []
        
        for port in self.common_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((target_ip, port)) == 0:
                    print(f"  {Fore.GREEN}↳ Found open port: {port}") # type: ignore
                    assets.append({
                        "ip": target_ip,
                        "port": port,
                        "service": "unknown",
                        "banner": "",
                        "hostnames": [],
                        "timestamp": None
                    })
        return assets