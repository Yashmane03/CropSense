import os
import json
import uuid
import sqlite3
import datetime
from typing import Dict, Any, List, Optional
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "crop_sense.db")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

class DatabaseService:
    def __init__(self):
        self.supabase_client: Optional[Client] = None
        self.use_supabase = False

        if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"):
            try:
                self.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
                self.use_supabase = True
                print(f"[DatabaseService] Initialized Supabase PostgreSQL connection to {SUPABASE_URL}")
            except Exception as e:
                print(f"[DatabaseService] Warning: Failed to connect to Supabase ({e}). Falling back to local SQLite database.")
                self.use_supabase = False

        if not self.use_supabase:
            print(f"[DatabaseService] Operating with SQLite database at {LOCAL_DB_PATH}")
            self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            analysis_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            crop TEXT NOT NULL,
            image_url TEXT NOT NULL,
            final_assessment TEXT NOT NULL,
            confidence TEXT NOT NULL,
            is_uncertain INTEGER NOT NULL,
            visual_predictions TEXT NOT NULL,
            weather_data TEXT NOT NULL,
            field_observations TEXT NOT NULL,
            evidence TEXT NOT NULL,
            advisory TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    async def save_analysis(
        self,
        crop: str,
        image_url: str,
        final_assessment: str,
        confidence: str,
        is_uncertain: bool,
        visual_predictions: dict,
        weather_data: dict,
        field_observations: dict,
        evidence: dict,
        advisory: dict,
        analysis_id: Optional[str] = None
    ) -> dict:
        if not analysis_id:
            analysis_id = str(uuid.uuid4())
        
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        record = {
            "analysis_id": analysis_id,
            "created_at": timestamp,
            "crop": crop,
            "image_url": image_url,
            "final_assessment": final_assessment,
            "confidence": confidence,
            "is_uncertain": 1 if is_uncertain else 0,
            "visual_predictions": json.dumps(visual_predictions),
            "weather_data": json.dumps(weather_data),
            "field_observations": json.dumps(field_observations),
            "evidence": json.dumps(evidence),
            "advisory": json.dumps(advisory)
        }

        if self.use_supabase and self.supabase_client:
            try:
                # Format for Supabase jsonb columns
                sb_record = {
                    "analysis_id": analysis_id,
                    "created_at": timestamp,
                    "crop": crop,
                    "image_url": image_url,
                    "final_assessment": final_assessment,
                    "confidence": confidence,
                    "is_uncertain": is_uncertain,
                    "visual_predictions": visual_predictions,
                    "weather_data": weather_data,
                    "field_observations": field_observations,
                    "evidence": evidence,
                    "advisory": advisory
                }
                res = self.supabase_client.table("analyses").insert(sb_record).execute()
                print(f"[DatabaseService] Analysis saved to Supabase: {analysis_id}")
            except Exception as e:
                print(f"[DatabaseService] Error saving to Supabase ({e}). Fallback saving to SQLite...")
                self._save_sqlite(record)
        else:
            self._save_sqlite(record)

        return {
            "analysis_id": analysis_id,
            "created_at": timestamp,
            "crop": crop,
            "image_url": image_url,
            "final_assessment": final_assessment,
            "confidence": confidence,
            "is_uncertain": is_uncertain,
            "visual_predictions": visual_predictions,
            "weather_data": weather_data,
            "field_observations": field_observations,
            "evidence": evidence,
            "advisory": advisory
        }

    def _save_sqlite(self, record: dict):
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO analyses (
                analysis_id, created_at, crop, image_url, final_assessment,
                confidence, is_uncertain, visual_predictions, weather_data,
                field_observations, evidence, advisory
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["analysis_id"], record["created_at"], record["crop"],
            record["image_url"], record["final_assessment"], record["confidence"],
            record["is_uncertain"], record["visual_predictions"], record["weather_data"],
            record["field_observations"], record["evidence"], record["advisory"]
        ))
        conn.commit()
        conn.close()

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[dict]:
        if self.use_supabase and self.supabase_client:
            try:
                res = self.supabase_client.table("analyses").select("*").eq("analysis_id", analysis_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                print(f"[DatabaseService] Supabase query error: {e}")

        # SQLite query
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE analysis_id = ?", (analysis_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        d = dict(row)
        return {
            "analysis_id": d["analysis_id"],
            "created_at": d["created_at"],
            "crop": d["crop"],
            "image_url": d["image_url"],
            "final_assessment": d["final_assessment"],
            "confidence": d["confidence"],
            "is_uncertain": bool(d["is_uncertain"]),
            "visual_predictions": json.loads(d["visual_predictions"]),
            "weather_data": json.loads(d["weather_data"]),
            "field_observations": json.loads(d["field_observations"]),
            "evidence": json.loads(d["evidence"]),
            "advisory": json.loads(d["advisory"])
        }

    async def get_history(self, limit: int = 50) -> List[dict]:
        if self.use_supabase and self.supabase_client:
            try:
                res = self.supabase_client.table("analyses").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return res.data
            except Exception as e:
                print(f"[DatabaseService] Supabase history query error: {e}")

        # SQLite query
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses ORDER BY datetime(created_at) DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            d = dict(r)
            results.append({
                "analysis_id": d["analysis_id"],
                "created_at": d["created_at"],
                "crop": d["crop"],
                "image_url": d["image_url"],
                "final_assessment": d["final_assessment"],
                "confidence": d["confidence"],
                "is_uncertain": bool(d["is_uncertain"]),
                "visual_predictions": json.loads(d["visual_predictions"]),
                "weather_data": json.loads(d["weather_data"]),
                "field_observations": json.loads(d["field_observations"]),
                "evidence": json.loads(d["evidence"]),
                "advisory": json.loads(d["advisory"])
            })
        return results

    async def upload_image(self, file_bytes: bytes, filename: str) -> str:
        unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"

        if self.use_supabase and self.supabase_client:
            try:
                # Ensure bucket exists
                try:
                    buckets = [b.name for b in self.supabase_client.storage.list_buckets()]
                    if "crop-images" not in buckets:
                        self.supabase_client.storage.create_bucket("crop-images", options={"public": True})
                except Exception as be:
                    print(f"[DatabaseService] Bucket check info: {be}")

                # Upload to Supabase Storage bucket 'crop-images'
                res = self.supabase_client.storage.from_("crop-images").upload(
                    path=unique_name,
                    file=file_bytes,
                    file_options={"content-type": "image/jpeg", "x-upsert": "true"}
                )
                public_url = self.supabase_client.storage.from_("crop-images").get_public_url(unique_name)
                print(f"[DatabaseService] Image uploaded to Supabase Storage: {public_url}")
                return public_url
            except Exception as e:
                print(f"[DatabaseService] Supabase Storage upload failed ({e}). Falling back to local storage.")

        # Local file storage fallback
        file_path = os.path.join(UPLOADS_DIR, unique_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        # Local server absolute URL
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        return f"{backend_url}/uploads/{unique_name}"

db_service = DatabaseService()
