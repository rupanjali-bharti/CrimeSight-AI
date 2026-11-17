"""Flexible retrieval of BNS sections from the Neo4j legal graph."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Protocol


class GraphQuery(Protocol):
    def query(
        self, query: str, params: Mapping[str, object] | None = None
    ) -> list[Mapping[str, object]]: ...


BNS_STATUTE_QUERY = """
MATCH (section:Entity)-[relationship]->(statute:Entity)
WHERE type(relationship) IN $statute_relationships
  AND toLower(coalesce(toString(section.type), '')) CONTAINS 'section'
  AND ANY(key IN keys(statute)
          WHERE toLower(toString(statute[key])) CONTAINS 'bharatiya nyaya sanhita'
             OR toLower(toString(statute[key])) = 'bns')
WITH section, statute,
     [keyword IN $keywords
      WHERE ANY(key IN keys(section)
                WHERE toLower(toString(section[key])) CONTAINS keyword)] AS matched_keywords
WHERE size(matched_keywords) > 0
RETURN properties(section) AS section_properties,
       properties(statute) AS statute_properties,
       matched_keywords
ORDER BY size(matched_keywords) DESC
LIMIT 12
"""


STATUTE_SEARCH_TERMS = {
    "commercial_contract_fraud": [
        "cheating",
        "fraud",
        "dishonestly",
        "contract",
        "agreement",
        "property",
        "breach of trust",
        "inducement",
    ],
    "cyber_fraud_impersonation": [
        "cheating",
        "deception",
        "personation",
        "identity theft",
        "electronic record",
        "forgery",
        "unauthorised access",
        "unauthorized access",
        "fraud",
        "impersonation",
        "hacking",
        "data breach",
        "phishing",
    ],
    "financial_fraud": [
        "cheating",
        "deception",
        "fraud",
        "dishonestly",
        "property",
        "personation",
    ],
    "cyber_harassment": [
        "stalking",
        "harassment",
        "criminal intimidation",
        "threat",
        "defamation",
        "privacy",
        "electronic",
    ],
    "assault": ["hurt", "assault", "voluntarily causing", "criminal force"],
    "theft": ["theft", "dishonestly", "movable property", "robbery"],
    "general": ["offence", "criminal intimidation", "hurt"],
}

STATUTE_RELATIONSHIPS = ["PART_OF_STATUTE", "PART_OF_ACT", "PART_OF"]


def _property(properties: Mapping[str, object], *keys: str) -> str:
    for key in keys:
        value = properties.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def normalize_statute_records(records: list[Mapping[str, object]]) -> list[dict[str, object]]:
    """Convert graph rows into a stable API-friendly statute shape."""
    statutes = []
    seen = set()
    for record in records:
        section_properties = record.get("section_properties") or {}
        statute_properties = record.get("statute_properties") or {}
        if not isinstance(section_properties, Mapping) or not isinstance(
            statute_properties, Mapping
        ):
            continue

        section = _property(
            section_properties,
            "section",
            "section_number",
            "section_no",
            "number",
            "name",
        )
        section = re.sub(r"^sections?\s+", "", section, flags=re.IGNORECASE)
        title = _property(section_properties, "title", "name", "heading")
        description = _property(
            section_properties, "description", "summary", "text", "provision"
        )
        statute_name = _property(
            statute_properties, "name", "title", "act_name", "statute"
        ) or "Bharatiya Nyaya Sanhita"
        if not title:
            title = description or (f"Section {section}" if section else "")

        identity = (section.casefold(), title.casefold(), statute_name.casefold())
        if identity in seen:
            continue
        seen.add(identity)
        statutes.append(
            {
                "section": section,
                "title": title,
                "statute": statute_name,
                "description": description,
                "matched_keywords": list(record.get("matched_keywords") or []),
            }
        )
    return statutes


def retrieve_bns_statutes(graph: GraphQuery, category: str) -> list[dict[str, object]]:
    """Search linked section properties for category-specific legal concepts."""
    keywords = STATUTE_SEARCH_TERMS.get(category, STATUTE_SEARCH_TERMS["general"])
    records = graph.query(
        BNS_STATUTE_QUERY,
        params={
            "keywords": keywords,
            "statute_relationships": STATUTE_RELATIONSHIPS,
        },
    )
    return normalize_statute_records(records)
