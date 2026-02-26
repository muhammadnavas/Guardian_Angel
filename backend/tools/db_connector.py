"""
MongoDB DatabaseConnector

Stores call analysis results in a MongoDB collection.
Set MONGO_URI in .env (defaults to a local instance).

Collection schema (one document per call):
    transcript         str   - full call transcript
    summary            str   - agent-generated summary
    threat_level       str   - SAFE / SUSPICIOUS / HIGH_RISK / CRITICAL
    threat_score       int   - 0-100
    caller_type        str   - optional, e.g. "scammer", "unknown"
    language           str   - detected language code
    fear_indicators    list  - matched fear keywords
    authority_indicators list
    urgency_indicators  list
    financial_indicators list
    alert_sent         bool  - whether family/police were alerted
    created_at         datetime
    transcript_hash    str   - SHA-256 for deduplication (unique index)
"""

import hashlib
import os
from datetime import datetime, timezone
from typing import Optional

from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


class DatabaseConnector:
    """Manages MongoDB operations for storing call analysis results."""

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: str = "guardian_angel",
        collection_name: str = "call_results",
    ):
        """Connect to MongoDB and ensure the unique index exists.

        Args:
            uri: MongoDB connection URI. Falls back to MONGO_URI env var,
                 then to 'mongodb://localhost:27017'.
            db_name: Database name.
            collection_name: Collection name.
        """
        resolved_uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self._client = MongoClient(resolved_uri, serverSelectionTimeoutMS=5000)
        self._col = self._client[db_name][collection_name]

        # Unique index prevents duplicate transcripts
        self._col.create_index("transcript_hash", unique=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store_result(
        self,
        transcript: str,
        summary: Optional[str],
        threat_level: str,
        threat_score: int,
        caller_type: Optional[str] = None,
        language: Optional[str] = None,
        fear_indicators: Optional[list] = None,
        authority_indicators: Optional[list] = None,
        urgency_indicators: Optional[list] = None,
        financial_indicators: Optional[list] = None,
        alert_sent: bool = False,
    ) -> Optional[str]:
        """Insert a call analysis document.

        Deduplicates by transcript hash — returns None if already stored.

        Returns:
            The inserted document's _id as a string, or None if duplicate.
        """
        doc = {
            "transcript": transcript,
            "summary": summary,
            "threat_level": threat_level,
            "threat_score": threat_score,
            "caller_type": caller_type,
            "language": language,
            "fear_indicators": fear_indicators or [],
            "authority_indicators": authority_indicators or [],
            "urgency_indicators": urgency_indicators or [],
            "financial_indicators": financial_indicators or [],
            "alert_sent": alert_sent,
            "created_at": datetime.now(timezone.utc),
            "transcript_hash": self._hash(transcript),
        }
        try:
            result = self._col.insert_one(doc)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return None

    def get_result(self, doc_id: str) -> Optional[dict]:
        """Retrieve a single document by its _id string."""
        from bson import ObjectId
        doc = self._col.find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def get_top_k(self, k: int = 10) -> list[dict]:
        """Return the k most recent call analysis documents."""
        docs = list(
            self._col.find({}, {"_id": 0, "transcript_hash": 0})
            .sort("created_at", DESCENDING)
            .limit(k)
        )
        return docs

    def get_all(self) -> list[dict]:
        """Return all documents sorted by recency."""
        return list(
            self._col.find({}, {"_id": 0, "transcript_hash": 0})
            .sort("created_at", DESCENDING)
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()