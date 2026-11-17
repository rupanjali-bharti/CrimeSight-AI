"""Narrative-based case categorization and evidence checklist matching."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping


EVIDENCE_REQUIREMENTS = {
    "commercial_contract_fraud": {
        "label": "Commercial / Contract Fraud",
        "indicators": [
            (
                r"\b(?:commercial|business|vendor|contractor|supplier|client)\b"
                r".{0,55}\b(?:contract|agreement|fraud|dispute|payment|"
                r"non[- ]delivery|withheld|handover|breach)\b",
                9,
            ),
            (
                r"\b(?:contract|agreement|invoice|deliverable|code handover|"
                r"project handover)\b.{0,55}\b(?:fraud|dispute|breach|"
                r"withheld|non[- ]delivery|not delivered|not paid|"
                r"commercial|business)\b",
                8,
            ),
            (
                r"\b(?:breach of contract|contract fraud|commercial fraud|"
                r"business dispute|contract dispute|non[- ]delivery of "
                r"(?:services|goods|code|work)|withheld source code)\b",
                12,
            ),
        ],
        "evidence": [
            (
                "Contracts / agreements and amendments",
                (
                    r"\b(?:signed|draft|executed|service|employment|vendor|"
                    r"commercial|written|original)?\s*(?:contract|agreement|"
                    r"mou|memorandum of understanding|statement of work|"
                    r"scope of work|terms and conditions)s?\b",
                    r"\b(?:contract|agreement)\s*(?:amendment|addendum|variation)s?\b",
                    r"\b(?:supporting|project|business|company|contractual)?\s*"
                    r"documents?\b",
                ),
            ),
            (
                "Emails / written correspondence",
                (
                    r"\b(?:email|e-mail|emails|correspondence|written "
                    r"communication|letter|message thread|text messages?)\b",
                    r"\b(?:sent|received|saved|exported|forwarded)\s+"
                    r"(?:the\s+)?(?:email|e-mail|correspondence|letters?)\b",
                ),
            ),
            (
                "Invoices / payment statements",
                (
                    r"\b(?:invoice|invoices|billing statement|account "
                    r"statement|bank statement|payment statement|receipt|"
                    r"payment confirmation|transaction record)s?\b",
                    r"\b(?:paid|payment|transfer)\b.{0,35}\b(?:invoice|"
                    r"statement|receipt|record|confirmation)\b",
                ),
            ),
            (
                "Deliverables / code handover records",
                (
                    r"\b(?:source code|code|software|project|work|"
                    r"deliverable|deliverables|repository|repo)\b.{0,60}"
                    r"\b(?:handover|hand over|transfer|delivery|delivered|"
                    r"commit|access|release|submission|records?|logs?)\b",
                    r"\b(?:handover|hand over|transfer|delivery|delivered|"
                    r"commit|access|release|submission)\b.{0,60}"
                    r"\b(?:source code|code|software|project|work|"
                    r"deliverable|repository|repo)\b",
                    r"\b(?:git|github|gitlab|bitbucket)\b.{0,50}"
                    r"\b(?:repository|repo|commit|access|handover|transfer)\b",
                ),
            ),
            (
                "Witness / meeting statements",
                (
                    r"\b(?:witness(?:es)?|eyewitness(?:es)?|witness "
                    r"statement|written statement|signed statement|"
                    r"affidavit|meeting minutes|minutes of meeting|"
                    r"meeting notes|testimony|deposition)\b",
                    r"\b(?:statement|minutes|notes|testimony)\b.{0,55}"
                    r"\b(?:from|by|of)\s+(?:[A-Z][\w'-]*|my\s+\w+|"
                    r"our\s+\w+|the\s+\w+)\b",
                ),
            ),
        ],
    },
    "cyber_fraud_impersonation": {
        "label": "Cyber Fraud / Impersonation",
        "indicators": [
            (
                r"\b(?:hack(?:ed|ing)?|unauthori[sz]ed access|account takeover|"
                r"data breach|data leak|phishing|stolen credentials|identity theft)\b",
                10,
            ),
            (
                r"\b(?:cyber fraud|online fraud|fraudulent website|"
                r"impersonat\w*|personation|spoof(?:ed|ing) identity)\b",
                7,
            ),
            (r"\b(?:fraud|scam|stolen money|unauthori[sz]ed transfer)\b", 3),
        ],
        "evidence": [
            (
                "Account security alerts / login notifications",
                (
                    r"\b(?:security|login|sign[\s-]?in|access)\s*(?:alert|notification|history|record)s?\b",
                    r"\b(?:account|password)\s*(?:recovery|reset)\s*(?:email|message|notice)?\b",
                ),
            ),
            (
                "Device, IP address / access logs",
                (
                    r"\b(?:device|ip address|access|login|server)\s*(?:logs?|history|records?)\b",
                    r"\bip address\b",
                ),
            ),
            (
                "Phishing / impersonation messages or links",
                (
                    r"\b(?:phishing|impersonat\w*|spoof\w*|fake)\b.{0,55}\b(?:message|email|sms|link|website|profile|account)\b",
                    r"\b(?:message|email|sms|link|website|profile|account)\b.{0,55}\b(?:phishing|impersonat\w*|spoof\w*|fake)\b",
                ),
            ),
            (
                "Financial transaction records, if money was lost",
                (
                    r"\b(?:bank|transaction|payment|transfer)\s*(?:statement|receipt|record|confirmation|alert)\b",
                    r"\b(?:utr|transaction id|reference number)\b",
                ),
            ),
        ],
    },
    "financial_fraud": {
        "label": "Financial / Money Fraud",
        "indicators": [
            (r"\b(?:upi|utr|bank debit|debit alert|transaction reference)\b", 6),
            (r"\b(?:transaction|money transfer|payment|bank account|wallet)\b", 4),
            (r"\b(?:fraud|scam|stolen money|unauthori[sz]ed transfer)\b", 3),
        ],
        "evidence": [
            (
                "SMS bank debit alert",
                (
                    r"\b(?:debit|credit|bank|transaction)\b.{0,45}\b(?:sms|text alert|alert)\b",
                    r"\b(?:sms|text alert|alert)\b.{0,45}\b(?:debit|credit|bank|transaction)\b",
                ),
            ),
            (
                "UTR / transaction reference number",
                (
                    r"\butr\b(?:\s*(?:number|no\.?|#))?(?:\s*[:#-]?\s*[a-z0-9-]{4,})?",
                    r"\b(?:transaction|txn)\s*(?:reference|ref|id|number|no\.?)\b",
                    r"\breference\s*(?:number|no\.?|#)\b",
                ),
            ),
            (
                "UPI merchant handle",
                (
                    r"\b(?:upi\s*(?:id|handle|address)|vpa|merchant handle)\b",
                    r"\b[a-z0-9._-]{2,}@[a-z][a-z0-9.-]*\b",
                ),
            ),
            (
                "Bank statement / payment receipt",
                (
                    r"\bbank statement\b",
                    r"\b(?:payment|transaction)\s*(?:receipt|confirmation)\b",
                    r"\breceipt\b",
                ),
            ),
        ],
    },
    "cyber_harassment": {
        "label": "Cyber Harassment / Stalking",
        "indicators": [
            (r"\b(?:cyber\s*stalk\w*|cyber\s*harass\w*)\b", 8),
            (r"\b(?:fake|impersonat\w*)\s+(?:social\s*media\s+)?profiles?\b", 7),
            (
                r"\b(?:stalk\w*|harass\w*|abusive messag\w*|threatening "
                r"(?:messages?|chats?|threads?)|defamat\w*|doxx?\w*|"
                r"cyberbully\w*|online abuse|repeated unwanted contact)\b",
                5,
            ),
            (r"\b(?:threats?|blackmail|unwanted messages?|impersonat\w*)\b", 4),
        ],
        "evidence": [
            (
                "Screenshots of fake profiles",
                (
                    r"\b(?:screenshots?|screen captures?|saved images?)\b.{0,70}\b(?:fake|impersonat\w*|profile|account)\b",
                    r"\b(?:fake|impersonat\w*|profile|account)\b.{0,70}\b(?:screenshots?|screen captures?|saved images?)\b",
                ),
            ),
            (
                "Threatening chat threads",
                (
                    r"\b(?:threat\w*|abusive|harassing)\b.{0,50}\b(?:chat|messages?|threads?|dm|conversation)\b",
                    r"\b(?:chat|messages?|threads?|dm|conversation)\b.{0,50}\b(?:threat\w*|abusive|harassing)\b",
                ),
            ),
            (
                "Call logs / phone numbers",
                (
                    r"\b(?:call logs?|call history|call timestamps?|caller id|phone numbers?|mobile numbers?)\b",
                    r"\b(?:calls?|called)\b.{0,35}\b(?:logs?|timestamps?|numbers?|recordings?)\b",
                ),
            ),
            (
                "Defamatory post links",
                (
                    r"\b(?:defamat\w*|offensive|threatening)\b.{0,50}\b(?:post|link|url)\b",
                    r"\b(?:post|link|url)\b.{0,50}\b(?:defamat\w*|offensive|threatening)\b",
                    r"\b(?:https?://|www\.)\S+",
                ),
            ),
        ],
    },
    "assault": {
        "label": "Assault / Physical Injury",
        "indicators": [
            (r"\b(?:assault|physical attack|grievous hurt|beaten|hit me|injur\w*|fight)\b", 5),
            (r"\b(?:punched|kicked|slapped|stabbed|struck)\b", 4),
        ],
        "evidence": [
            (
                "Medical records / injury photographs",
                (
                    r"\b(?:medical|hospital|injury)\s*(?:report|record|photo|photograph|image)s?\b",
                    r"\b(?:m\*?lc|medico legal certificate)\b",
                ),
            ),
            ("Witness details / statements", (r"\b(?:witness(?:es)?|eyewitness)\b",)),
            ("CCTV / video footage", (r"\b(?:cctv|camera|security)\s*(?:video|footage|recording)\b",)),
            ("Incident time and location", (r"\b(?:incident|attack|assault)\s+(?:time|location|place)\b",)),
        ],
    },
    "theft": {
        "label": "Theft / Property Offence",
        "indicators": [
            (r"\b(?:theft|stolen|robbery|burglary|snatched|shoplift\w*)\b", 5),
            (r"\b(?:missing|taken|property)\b", 2),
        ],
        "evidence": [
            (
                "Proof of ownership / purchase records",
                (
                    r"\b(?:proof|document|record)s?\s+of\s+ownership\b",
                    r"\b(?:purchase|sales?)\s*(?:receipt|invoice|record)s?\b",
                ),
            ),
            ("Property identifiers", (r"\b(?:serial number|imei|registration number|identifying marks)\b",)),
            ("CCTV / video footage", (r"\b(?:cctv|camera|security)\s*(?:video|footage|recording)\b",)),
            ("Witness details / statements", (r"\b(?:witness(?:es)?|eyewitness)\b",)),
        ],
    },
    "general": {
        "label": "General Incident",
        "indicators": [],
        "evidence": [
            ("Incident time and location", (r"\b(?:incident|event)\s+(?:time|location|place)\b",)),
            ("Witness details / statements", (r"\b(?:witness(?:es)?|eyewitness)\b",)),
            ("Photos / video / CCTV", (r"\b(?:photo|photograph|video footage|cctv|camera footage)\b",)),
            ("Medical records, if relevant", (r"\b(?:medical|hospital|injury)\s*(?:report|record|photo)s?\b",)),
        ],
    },
}

NEGATION_PATTERN = re.compile(
    r"\b(?:no|not|never|don't|do not|doesn't|does not|haven't|have not|"
    r"hasn't|has not|missing|unavailable|unable to (?:find|provide|access|retrieve)|yet to)\b"
    r"[^.!?\n]{0,55}$",
    re.IGNORECASE,
)

INCIDENT_TIME_PATTERNS = (
    r"\b(?:at|around|about|approximately|by)\s+\d{1,2}(?::\d{2})?\s*"
    r"(?:a\.?m\.?|p\.?m\.?|hrs?|o'clock)\b",
    r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|hrs?)\b",
    r"\b(?:yesterday|today|last night|last evening|this morning|"
    r"this afternoon|this evening|early morning|late night|at noon|at midnight)\b",
    r"\b(?:on|since|until|during)\s+(?:monday|tuesday|wednesday|thursday|"
    r"friday|saturday|sunday|yesterday|today)\b",
    r"\b(?:on\s+)?\d{1,2}(?:st|nd|rd|th)?\s+"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)(?:\s*,?\s*\d{4})?\b",
    r"\b\d{4}-\d{1,2}-\d{1,2}\b",
)

INCIDENT_LOCATION_PATTERNS = (
    r"\b(?:at|near|outside|inside|in front of|opposite|behind|from|in)\s+"
    r"(?:the\s+)?(?:my\s+)?(?:home|house|residence|office|workplace|school|"
    r"college|university|market|shop|store|station|bus stop|railway station|"
    r"police station|hospital|clinic|park|parking lot|parking area|street|"
    r"road|highway|bridge|building|apartment|restaurant|bank|court|hotel|"
    r"playground|neighborhood|neighbourhood)\b",
    r"\b(?:on|along|near|outside|at)\s+(?:the\s+)?"
    r"(?:[a-z][\w'-]*\s+){0,3}(?:street|road|lane|avenue|highway|"
    r"crossing|junction|square|park|market|village|district)\b",
)
PROPER_PLACE_PATTERN = re.compile(
    r"\b(?:at|near|outside|inside|in front of|opposite|behind|from|in)\s+"
    r"(?:the\s+)?([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,3})\b"
)
NON_PLACE_NAMES = {
    "afternoon",
    "evening",
    "morning",
    "night",
    "noon",
    "midnight",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
}

WITNESS_PATTERNS = (
    r"\b(?:witness(?:es)?|eyewitness(?:es)?)\b",
    r"\b(?:statement|testimony|account)\s+from\s+"
    r"(?:[A-Z][\w'-]*|my\s+\w+|a\s+\w+|our\s+\w+)\b",
    r"\b(?:my|our|a|the)\s+(?:friend|colleague|coworker|co-worker|"
    r"neighbor|neighbour|family member|relative|brother|sister|"
    r"mother|father|partner|classmate|roommate)\b"
    r"[^.!?;]{0,90}\b(?:saw|seen|witness\w*|observed|heard|"
    r"was present|was there|was with me)\b",
    r"\b(?:saw|witness\w*|observed|heard)\b"
    r"[^.!?;]{0,70}\b(?:my|our|a|the)\s+(?:friend|colleague|coworker|"
    r"co-worker|neighbor|neighbour|family member|relative|"
    r"brother|sister|mother|father|partner|classmate|roommate)\b",
    r"\b(?!I\b|He\b|She\b|We\b|They\b|It\b|My\b|The\b|This\b|That\b)"
    r"[A-Z][a-z'-]{1,30}\s+(?:witnessed|observed|saw|heard)\b",
)


def _user_turns(
    current_situation: str, chat_history: Iterable[Mapping[str, str]] | None
) -> list[str]:
    turns = [
        message.get("content", "").strip()
        for message in (chat_history or [])
        if message.get("role", "user").strip().lower() == "user"
        and message.get("content", "").strip()
    ]
    if current_situation.strip() and (
        not turns or turns[-1] != current_situation.strip()
    ):
        turns.append(current_situation.strip())
    return turns


def _category_scores(text: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    for category, definition in EVIDENCE_REQUIREMENTS.items():
        score = sum(
            len(re.findall(pattern, text, re.IGNORECASE)) * weight
            for pattern, weight in definition["indicators"]
        )
        if score:
            scores[category] = score
    return scores


def classify_case_category(text: str) -> str:
    """Re-evaluate user turns, weighting recent explicit category changes."""
    turns = [turn.strip() for turn in text.splitlines() if turn.strip()]
    if not turns:
        return "general"

    scores: dict[str, float] = {}
    for index, turn in enumerate(turns):
        recency_weight = 0.65 ** (len(turns) - index - 1)
        current_scores = _category_scores(turn)
        if index == len(turns) - 1:
            recency_weight = 3.0
        for category, score in current_scores.items():
            scores[category] = scores.get(category, 0.0) + score * recency_weight

    if not scores:
        return "general"
    priority = (
        "commercial_contract_fraud",
        "cyber_fraud_impersonation",
        "cyber_harassment",
        "financial_fraud",
        "assault",
        "theft",
    )
    return max(priority, key=lambda category: scores.get(category, 0.0))


def _evidence_is_available(turns: list[str], patterns: tuple[str, ...]) -> bool:
    available = False
    for turn in turns:
        for clause in re.finditer(r"[^,;.!?]+", turn):
            clause_text = clause.group()
            matches = sorted(
                (
                    match
                    for pattern in patterns
                    for match in re.finditer(pattern, clause_text, re.IGNORECASE)
                ),
                key=lambda match: match.start(),
            )
            for match in matches:
                prefix = clause_text[max(0, match.start() - 65) : match.start()]
                available = not bool(NEGATION_PATTERN.search(prefix))
    return available


def _incident_time_and_location_is_available(turns: list[str]) -> bool:
    time_available = _evidence_is_available(turns, INCIDENT_TIME_PATTERNS)
    location_available = _evidence_is_available(turns, INCIDENT_LOCATION_PATTERNS)

    if not location_available:
        for turn in turns:
            for match in PROPER_PLACE_PATTERN.finditer(turn):
                place = match.group(1).strip().casefold()
                if place in NON_PLACE_NAMES:
                    continue
                prefix = turn[max(0, match.start() - 65) : match.start()]
                if not NEGATION_PATTERN.search(prefix):
                    location_available = True
                else:
                    location_available = False

    return time_available and location_available


def analyze_case_evidence(
    current_situation: str,
    chat_history: Iterable[Mapping[str, str]] | None = None,
) -> dict[str, object]:
    """Classify all user turns and assess evidence explicitly mentioned in them."""
    turns = _user_turns(current_situation, chat_history)
    category = classify_case_category("\n".join(turns))
    definition = EVIDENCE_REQUIREMENTS[category]

    checklist = []
    for label, patterns in definition["evidence"]:
        if label == "Witness details / statements":
            available = _evidence_is_available(turns, WITNESS_PATTERNS)
        elif label == "Incident time and location":
            available = _incident_time_and_location_is_available(turns)
        else:
            available = _evidence_is_available(turns, patterns)
        checklist.append(
            {"item": label, "status": "AVAILABLE" if available else "MISSING"}
        )

    fir_ready = bool(checklist) and all(
        item["status"] == "AVAILABLE" for item in checklist
    )
    return {
        "category": category,
        "category_label": definition["label"],
        "evidence_checklist": checklist,
        "fir_ready": fir_ready,
    }
