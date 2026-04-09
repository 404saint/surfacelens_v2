import os
from datetime import datetime

class Reporter:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_markdown(self, target, assets_with_findings):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{self.output_dir}/report_{target}_{timestamp}.md"
        
        with open(filename, "w") as f:
            f.write(f"# SurfaceLens V2 Intelligence Report\n")
            f.write(f"**Target:** {target}  \n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
            f.write(f"--- \n\n")
            
            for item in assets_with_findings:
                asset = item['asset']
                final = item['risk']
                
                f.write(f"## {asset['ip']}:{asset['port']}\n")
                f.write(f"- **Priority:** {final['priority']} (Score: {final['final_score']})\n")
                f.write(f"- **Service:** {asset.get('service', 'unknown')}\n")
                
                if final['risk_factors']:
                    f.write("### Risk Factors\n")
                    for factor in final['risk_factors']:
                        f.write(f"- {factor}\n")
                f.write("\n---\n")
                
        print(f"\n[+] Report generated: {filename}")