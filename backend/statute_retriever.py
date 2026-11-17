
STATUTE_DATA = {
    "commercial_contract_fraud": [
        {
            "section": "Section 318",
            "title": "Cheating",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with cheating, including deception and dishonest inducement to deliver property or cause another person to act or omit to act.",
        },
        {
            "section": "Section 316",
            "title": "Criminal breach of trust",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with dishonest misappropriation or conversion of property entrusted to a person.",
        },
        {
            "section": "Section 314",
            "title": "Dishonest misappropriation of property",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with dishonest misappropriation or conversion of movable property.",
        },
    ],

    "cyber_fraud_impersonation": [
        {
            "section": "Section 318",
            "title": "Cheating",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with deception and dishonest inducement.",
        },
        {
            "section": "Section 319",
            "title": "Cheating by personation",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with cheating by pretending to be another person or knowingly substituting one person for another.",
        },
        {
            "section": "Section 336",
            "title": "Forgery",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with making a false document or false electronic record with the intent specified in the section.",
        },
    ],

    "financial_fraud": [
        {
            "section": "Section 318",
            "title": "Cheating",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with cheating and dishonest inducement.",
        },
        {
            "section": "Section 316",
            "title": "Criminal breach of trust",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with dishonest use or disposal of entrusted property.",
        },
    ],

    "cyber_harassment": [
        {
            "section": "Section 351",
            "title": "Criminal intimidation",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with threats intended to cause alarm or compel a person to do or omit an act.",
        },
        {
            "section": "Section 356",
            "title": "Defamation",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with making or publishing imputations that harm a person's reputation, subject to the statutory provisions and exceptions.",
        },
    ],

    "assault": [
        {
            "section": "Section 115",
            "title": "Voluntarily causing hurt",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with voluntarily causing hurt.",
        },
        {
            "section": "Section 131",
            "title": "Punishment for assault or criminal force otherwise than on grave provocation",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with assault or criminal force in the circumstances specified in the section.",
        },
    ],

    "theft": [
        {
            "section": "Section 303",
            "title": "Theft",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with dishonest taking of movable property out of another person's possession without consent.",
        },
        {
            "section": "Section 304",
            "title": "Snatching",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with theft involving sudden or forcible seizure, taking or grabbing of movable property from a person or their possession.",
        },
    ],

    "general": [
        {
            "section": "Section 351",
            "title": "Criminal intimidation",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with criminal intimidation.",
        },
        {
            "section": "Section 318",
            "title": "Cheating",
            "statute": "Bharatiya Nyaya Sanhita, 2023",
            "description": "Deals with cheating.",
        },
    ],
}


def retrieve_bns_statutes(graph, category: str) -> list[dict]:
    """Return predefined BNS sections for a category."""
    return STATUTE_DATA.get(category, STATUTE_DATA["general"])
