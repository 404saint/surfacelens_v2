from core.plugin_base import IntelligenceModule # type: ignore

class RiskPrioritizer(IntelligenceModule):
    @property
    def name(self) -> str:
        return "Risk Prioritizer"

    def run(self, asset: dict, module_results: list) -> dict:
        """
        Calculates a weighted risk score based on aggregated module results.
        Scale: 0.0 (Safe) to 10.0 (Critical)
        """
        base_score = 0.0
        factors = []
        
        # 1. Evaluate Port/Service Risk
        port = asset.get('port')
        high_risk_ports = {3389: 4.0, 445: 4.5, 21: 3.0, 23: 4.0, 3306: 3.5}
        
        if port in high_risk_ports:
            impact = high_risk_ports[port]
            base_score += impact
            factors.append(f"High-risk port exposed ({port})")

        # 2. Aggregate Deltas from other modules
        for result in module_results:
            delta = result.get("risk_delta", 0.0)
            if delta > 0:
                base_score += delta
                factors.extend(result.get("issues", []))

        # 3. Cap and Normalize
        final_score = min(round(base_score, 1), 10.0)
        
        # 4. Determine Priority Level
        priority = "LOW"
        if final_score >= 8.0: priority = "CRITICAL"
        elif final_score >= 6.0: priority = "HIGH"
        elif final_score >= 4.0: priority = "MEDIUM"

        return {
            "module": self.name,
            "final_score": final_score,
            "priority": priority,
            "risk_factors": list(set(factors))
        }