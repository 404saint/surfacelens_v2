import os
import sys
from colorama import Fore, Style, init

# Core & All Providers
from core.engine import Engine
from providers.leakix_p import LeakIXProvider
from providers.local_json_p import LocalJSONProvider
from providers.active_scan_p import ActiveScanProvider
from providers.shodan_p import ShodanProvider
from providers.censys_p import CensysProvider
from providers.criminalip_p import CriminalIPProvider

# All Intelligence Modules
from modules.ssl_auditor import SSLAuditor
from modules.dns_correlator import DNSCorrelator
from modules.delta_engine import DeltaEngine
from modules.risk_prioritizer import RiskPrioritizer
from modules.hunter import Hunter
from modules.fingerprinter import Fingerprinter
from modules.reporter import Reporter

init(autoreset=True)

def print_banner():
    banner = rf"""
    {Fore.CYAN}{Style.BRIGHT}   _____              __                __                      
    {Fore.CYAN}{Style.BRIGHT}  / ___/__  _________ _/ /__  ____  _____/ /   ___  ____  _____   
    {Fore.CYAN}{Style.BRIGHT}  \__ \/ / / / ___/ __ `/ / _ \/ __ \/ ___/ /   / _ \/ __ \/ ___/   
    {Fore.CYAN}{Style.BRIGHT} ___/ / /_/ / /  / /_/ / /  __/ / / (__  ) /___/  __/ / / (__  )    
    {Fore.CYAN}{Style.BRIGHT}/____/\__,_/_/   \__,_/_/\___/_/ /_/____/_____/\___/_/ /_/____/ v2.0
    
    {Fore.YELLOW}          -- Tactical Attack Surface & Shadow IT Sentinel --
    """
    print(banner)

def main():
    print_banner()
    engine = Engine()
    
    # NEW: Quick Reset Check
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        confirm = input(f"{Fore.RED}[!] Are you sure you want to wipe the database? (y/n): ")
        if confirm.lower() == 'y':
            # Access the .conn attribute of our Database object
            engine.db.conn.execute("DELETE FROM assets")
            engine.db.conn.commit()
            print(f"{Fore.GREEN}[+] Database cleared. Starting fresh.")
            return  # Exit after reset so we don't start a scan immediately
        else:
            print(f"{Fore.YELLOW}[*] Reset cancelled.")
            return

    # --- STEP 1: DYNAMIC PROVIDER REGISTRATION ---
    provider_config = {
        "leakix": (LeakIXProvider, ["LEAKIX_API_KEY"]),
        "shodan": (ShodanProvider, ["SHODAN_API_KEY"]),
        "censys": (CensysProvider, ["CENSYS_API_ID", "CENSYS_API_SECRET"]),
        "criminalip": (CriminalIPProvider, ["CRIMINALIP_API_KEY"]),
        "local": (LocalJSONProvider, []),
        "active": (ActiveScanProvider, [])
    }

    available_display = []
    for name, (cls, env_keys) in provider_config.items():
        try:
            # Safely register even if keys are missing
            engine.register_provider(name, cls())
            
            # Check keys only for the UI status
            has_keys = all(os.getenv(k) for k in env_keys) if env_keys else True
            status = "" if has_keys else f"{Fore.RED}(No Key)"
            available_display.append(f"{Fore.WHITE}{name}{status}")
        except Exception as e:
            available_display.append(f"{Fore.RED}{name}(Load Error)")

    # --- STEP 2: MODULE INITIALIZATION ---
    ssl_mod = SSLAuditor()
    dns_mod = DNSCorrelator()
    delta_mod = DeltaEngine()
    risk_mod = RiskPrioritizer()
    hunt_mod = Hunter()
    finger_mod = Fingerprinter()

    print(f"\n{Fore.MAGENTA}[#] Systems Online: {', '.join(available_display)}")
    p_choice = input(f"{Fore.WHITE}Select Provider: ").strip().lower()
    
    if p_choice not in engine.providers:
        print(f"{Fore.RED}[!] Invalid provider.")
        return

    query = input(f"{Fore.WHITE}Enter Target (e.g., example.com, ip address, hostname, etc.): ").strip()
    target_dom = input(f"{Fore.WHITE}Corporate Domain: ").strip()

    print(f"\n{Fore.BLUE}{Style.BRIGHT}[STAGE 1] DISCOVERY")
    raw_assets = engine.run_discovery(p_choice, query)
    
    if not raw_assets:
        print(f"{Fore.RED}[!] Discovery failed to find assets.")
        return

    print(f"\n{Fore.BLUE}{Style.BRIGHT}[STAGE 2] INTELLIGENCE PIPELINE")
    report_data = []

    for asset in raw_assets:
        ip_p = f"{asset['ip']}:{asset['port']}"
        print(f"\n{Fore.YELLOW}🔍 Analyzing: {Style.BRIGHT}{ip_p}")
        
        # Execution
        d_res = delta_mod.run(asset, engine.db)
        s_res = ssl_mod.run(asset)
        n_res = dns_mod.run(asset, target_dom)
        h_res = hunt_mod.run(asset)
        f_res = finger_mod.run(asset)
        
        # Scoring
        final = risk_mod.run(asset, [d_res, s_res, n_res, h_res, f_res])
        
        # Display
        status_txt = f"{Fore.MAGENTA}[NEW]" if d_res['is_new'] else f"{Fore.GREEN}[KNOWN]"
        print(f"  {status_txt} First Seen: {d_res['first_seen']}")

        if n_res.get('reverse_dns'):
            attr_txt = f"{Fore.CYAN}(Affiliated)" if n_res.get('is_affiliated') else f"{Fore.RED}(EXTERNAL/SHADOW)"
            print(f"  {Fore.CYAN}↳ PTR: {n_res['reverse_dns']} {attr_txt}")

        if s_res.get('cert_present'):
            print(f"  {Fore.BLUE}↳ SSL: {s_res['protocol']} detected")

        if f_res.get('software') and f_res.get('software') != "Unknown":
            print(f"  {Fore.BLUE}↳ Server: {f_res['software']}")

        if h_res.get('discovered_files'):
            print(f"  {Fore.RED}{Style.BRIGHT}↳ CRITICAL: Files Exposed ({', '.join(h_res['discovered_files'])})")

        priority = final.get('priority', 'LOW')
        p_color = { "CRITICAL": Fore.RED + Style.BRIGHT, "HIGH": Fore.RED, "MEDIUM": Fore.YELLOW }.get(priority, Fore.GREEN)
        score = final.get('final_score', 0)
        print(f"  {p_color}↳ PRIORITY: {priority} (Score: {score}/10)")
        
        for factor in final.get('risk_factors', []):
            print(f"    {Fore.WHITE}- {factor}")

        report_data.append({'asset': asset, 'risk': final})

    print(f"\n{Fore.BLUE}{Style.BRIGHT}[STAGE 3] EXPORT")
    if input(f"{Fore.WHITE}Generate Markdown Report? (y/n): ").lower() == 'y':
        Reporter().generate_markdown(query, report_data)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] User interrupted. Cleaning up and exiting...")
        # Optional: any database commit or cleanup code goes here
        sys.exit(0)