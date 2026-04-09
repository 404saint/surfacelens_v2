import sqlite3
import json
from datetime import datetime, timezone

class Database:
    def __init__(self, db_path="surfacelens.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Creates the assets table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            ip TEXT,
            port INTEGER,
            service TEXT,
            risk_score REAL,
            last_seen TIMESTAMP,
            raw_data TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def upsert_asset(self, asset):
        """Adds a new asset or updates an existing one."""
        # Unique ID is IP:Port
        asset_id = f"{asset.get('ip')}:{asset.get('port')}"
        now = datetime.now(timezone.utc).isoformat()
        
        query = """
        INSERT INTO assets (id, ip, port, service, risk_score, last_seen, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            service=excluded.service,
            risk_score=excluded.risk_score,
            last_seen=excluded.last_seen,
            raw_data=excluded.raw_data
        """
        self.conn.execute(query, (
            asset_id,
            asset.get('ip'),
            asset.get('port'),
            asset.get('service'),
            asset.get('risk_score', 0.0),
            now,
            json.dumps(asset)
        ))
        self.conn.commit()

    def get_all_assets(self):
        """Retrieves everything for reporting."""
        cursor = self.conn.execute("SELECT raw_data FROM assets")
        return [json.loads(row[0]) for row in cursor.fetchall()]