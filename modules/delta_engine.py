from core.plugin_base import IntelligenceModule # type: ignore
from datetime import datetime, timedelta, timezone

class DeltaEngine(IntelligenceModule):
    @property
    def name(self) -> str:
        return "Delta Engine"

    def run(self, asset: dict, db_instance) -> dict:
        """
        Compares the current asset against the database history.
        """
        asset_id = f"{asset.get('ip')}:{asset.get('port')}"
        findings = {
            "module": self.name,
            "status": "Existing",
            "is_new": False,
            "risk_delta": 0.0,
            "first_seen": None
        }

        # Query the DB for this specific ID
        cursor = db_instance.conn.execute(
            "SELECT last_seen FROM assets WHERE id = ?", (asset_id,)
        )
        row = cursor.fetchone()

        if not row:
            # Not in DB? It's a brand new discovery!
            findings["status"] = "NEW ASSET"
            findings["is_new"] = True
            findings["risk_delta"] = 2.0  # New assets are inherently riskier/unknown
            findings["first_seen"] = datetime.now(timezone.utc).isoformat()
        else:
            findings["first_seen"] = row[0]
            
        return findings