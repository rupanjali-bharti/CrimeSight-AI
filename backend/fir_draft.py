"""Compile user-provided case details into a review-ready FIR draft."""

from collections.abc import Mapping, Sequence
import re


def checklist_is_complete(evidence_checklist: Sequence[Mapping[str, str]]) -> bool:
    return bool(evidence_checklist) and all(
        item.get("status") == "AVAILABLE" for item in evidence_checklist
    )


def extract_case_details(case_narrative: str) -> dict[str, str]:
    """Extract explicitly stated details; leave uncertain values for review."""
    details = {
        "complainant_name": "",
        "police_station": "",
        "district_city": "",
        "incident_date": "",
        "incident_time": "",
        "incident_location": "",
    }
    text = case_narrative

    name_patterns = (
        r"\bmy name is\s+([A-Z][a-z]+(?:[ '-][A-Z][a-z]+){0,3})",
        r"\bi am\s+([A-Z][a-z]+(?:[ '-][A-Z][a-z]+){0,3})\b"
        r"(?=\s*(?:[,.;\n]|$|\b(?:and|from|,)\b))",
        r"\bi'm\s+([A-Z][a-z]+(?:[ '-][A-Z][a-z]+){0,3})\b"
        r"(?=\s*(?:[,.;\n]|$|\b(?:and|from)\b))",
    )
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details["complainant_name"] = match.group(1).strip()
            break

    station_match = re.search(
        r"\b(?:at|in|to|for|under|within|jurisdiction of)\s+"
        r"([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,4}\s+"
        r"Police\s+Station)\b",
        text,
        re.IGNORECASE,
    )
    if not station_match:
        station_match = re.search(
            r"\b([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,4}\s+"
            r"Police\s+Station)\b",
            text,
            re.IGNORECASE,
        )
    if station_match:
        details["police_station"] = station_match.group(1).strip()

    city_patterns = (
        r"\b(?:district|city|town)\s+(?:of|is|:)\s+"
        r"([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,3})",
        r"\b(?:in|at|near|from)\s+"
        r"(Bengaluru|Bangalore|Mumbai|Delhi|New Delhi|Chennai|Kolkata|"
        r"Hyderabad|Pune|Ahmedabad|Jaipur|Lucknow|Bhopal|Chandigarh|"
        r"Kochi|Thiruvananthapuram|Mysuru|Mysore)\b",
    )
    for pattern in city_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            details["district_city"] = matches[-1].group(1).strip()
            break

    date_patterns = (
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+"
        r"(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s*,?\s*\d{4}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}-\d{1,2}-\d{1,2}\b",
        r"\b(?:yesterday|today|last night|last evening|this morning|"
        r"this afternoon|this evening)\b",
    )
    for pattern in date_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            details["incident_date"] = matches[-1].group(0).strip()
            break

    time_patterns = (
        r"\b\d{1,2}(?::\d{2})\s*(?:a\.?m\.?|p\.?m\.?)\b",
        r"\b\d{1,2}\s*(?:a\.?m\.?|p\.?m\.?)\b",
        r"\b(?:around|about|at)\s+\d{1,2}(?::\d{2})?\s*"
        r"(?:a\.?m\.?|p\.?m\.?|hrs?)\b",
    )
    for pattern in time_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            details["incident_time"] = matches[-1].group(0).strip()
            break

    location_patterns = (
        r"\b(?:at|near|outside|inside|in front of|opposite|behind)\s+"
        r"(?:the\s+)?([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,3})"
        r"(?=\s*(?:[,.;\n]|$|\b(?:in|at|near|on)\b))",
        r"\b(?:at|near|outside|inside|in front of|opposite|behind)\s+"
        r"(?:the\s+)?((?:my\s+)?(?:home|house|office|workplace|school|"
        r"college|market|shop|station|hospital|park|street|road|"
        r"restaurant|bank|hotel))\b",
    )
    for pattern in location_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            location = matches[-1].group(1).strip()
            city = details["district_city"]
            if city:
                location = re.sub(
                    rf"\s+(?:in|at|near)\s+{re.escape(city)}$",
                    "",
                    location,
                    flags=re.IGNORECASE,
                )
            details["incident_location"] = location
            break

    return details


def compile_fir_draft(
    case_narrative: str,
    category_label: str,
    evidence_checklist: Sequence[Mapping[str, str]],
    matched_statutes: Sequence[Mapping[str, object]],
    case_details: Mapping[str, str] | None = None,
) -> str:
    """Format reported facts without adding details or unsupported legal claims."""
    case_details = case_details or extract_case_details(case_narrative)
    available_evidence = [
        item.get("item", "").strip()
        for item in evidence_checklist
        if item.get("status") == "AVAILABLE" and item.get("item", "").strip()
    ]
    statute_lines = []
    for statute in matched_statutes:
        section = str(statute.get("section") or "").strip()
        title = str(statute.get("title") or "").strip()
        name = str(statute.get("statute") or "Bharatiya Nyaya Sanhita").strip()
        citation = f"{name} Section {section}" if section else name
        if title and title.casefold() not in citation.casefold():
            citation = f"{citation} — {title}"
        if citation not in statute_lines:
            statute_lines.append(citation)

    statutes_text = (
        "\n".join(f"- {line}" for line in statute_lines)
        if statute_lines
        else "- No matching BNS section was returned by the connected statute graph."
    )
    evidence_text = (
        "\n".join(f"- {item}" for item in available_evidence)
        if available_evidence
        else "- No evidence items were marked as mentioned."
    )
    narrative = case_narrative.strip() or "[Incident details to be provided]"
    police_station = case_details.get("police_station") or "[Police Station]"
    district_city = case_details.get("district_city") or "[District / City]"
    complainant_name = case_details.get("complainant_name") or "[Full name]"
    complainant_signature = case_details.get("complainant_name") or "[Full name]"
    incident_date = case_details.get("incident_date") or "[To be confirmed]"
    incident_time = case_details.get("incident_time") or "[To be confirmed]"
    incident_location = case_details.get("incident_location") or "[To be confirmed]"

    return f"""DRAFT COMPLAINT FOR REGISTRATION OF FIR
(For review and completion before submission)

To
The Station House Officer
{police_station}
{district_city}

Subject: Request to record a complaint regarding {category_label}

Complainant: {complainant_name}
Address / contact: [Address and contact details]
Date of complaint: [Date]

Respected Sir/Madam,

I request that my complaint concerning the incident described below be recorded
and dealt with in accordance with applicable law.

1. INCIDENT AS REPORTED
{narrative}

Date and time of incident: {incident_date}, {incident_time}
Place of incident: {incident_location}
Person(s) involved, if known: [To be provided]

2. EVIDENCE REPORTED AS AVAILABLE
{evidence_text}

3. POTENTIALLY RELEVANT BNS REFERENCES
{statutes_text}

I request that the information be examined, relevant records be preserved where
appropriate, and any further steps be taken in accordance with law. The facts and
supporting materials should be checked and completed before this draft is submitted.

Yours faithfully,

[Complainant's signature]
{complainant_signature}
[Date]

Drafting note: This document is an organizational draft based only on information
provided in the chat and graph-retrieved references. It is not a filed FIR, a
finding of fact, or legal advice. Please verify all details and statutory
references with the investigating authority or a qualified legal professional."""
