"""Market intelligence ingestion scaffolds for external sources."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MarketIntelligenceIngestionService:
    """Stub ingestion service for market intelligence sources."""

    @staticmethod
    def fetch_telegram_signals() -> List[Dict[str, Any]]:
        """Placeholder for Telegram ingestion."""
        logger.info("Telegram ingestion scaffold invoked")
        return []

    @staticmethod
    def fetch_google_trends_signals() -> List[Dict[str, Any]]:
        """Placeholder for Google Trends ingestion."""
        logger.info("Google Trends ingestion scaffold invoked")
        return []

    @staticmethod
    def fetch_reddit_signals() -> List[Dict[str, Any]]:
        """Placeholder for Reddit ingestion."""
        logger.info("Reddit ingestion scaffold invoked")
        return []

    @staticmethod
    def fetch_x_signals() -> List[Dict[str, Any]]:
        """Placeholder for X/Twitter ingestion."""
        logger.info("X ingestion scaffold invoked")
        return []

    @classmethod
    def ingest(cls, company_id: int | None, include_placeholders: bool = True) -> List[Dict[str, Any]]:
        """Aggregate signals from all sources with optional placeholders."""
        signals = []
        signals.extend(cls.fetch_telegram_signals())
        signals.extend(cls.fetch_google_trends_signals())
        signals.extend(cls.fetch_reddit_signals())
        signals.extend(cls.fetch_x_signals())

        if not signals and include_placeholders:
            return cls._placeholder_signals(company_id)

        return signals

    @staticmethod
    def _placeholder_signals(company_id: int | None) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        placeholder_company_id = company_id or 0
        return [
            {
                "company_id": placeholder_company_id,
                "source": "trends",
                "signal_type": "demand_shift",
                "title": "Rising interest in premium bundles",
                "summary": "Search volume for premium bundles climbed week over week.",
                "severity": "medium",
                "signal_date": now,
                "raw_data": {"note": "Placeholder signal until ingestion is configured"},
                "is_actionable": True,
            },
            {
                "company_id": placeholder_company_id,
                "source": "reddit",
                "signal_type": "sentiment",
                "title": "Community threads highlight pricing sensitivity",
                "summary": "Multiple threads mention discount expectations in the category.",
                "severity": "high",
                "signal_date": now,
                "raw_data": {"note": "Placeholder signal until ingestion is configured"},
                "is_actionable": True,
            },
        ]
