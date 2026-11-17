const evidenceByCategory = {
  commercial_contract_fraud: {
    label: "Commercial / Contract Fraud",
    requirements: [
      {
        label: "Contracts / agreements and amendments",
        signals: ["contract", "agreement", "mou", "statement of work", "scope of work", "contract amendment"],
      },
      {
        label: "Emails / written correspondence",
        signals: ["email", "e-mail", "correspondence", "written communication", "letter", "message thread"],
      },
      {
        label: "Invoices / payment statements",
        signals: ["invoice", "billing statement", "account statement", "bank statement", "payment statement", "receipt"],
      },
      {
        label: "Deliverables / code handover records",
        signals: ["source code", "code handover", "project handover", "repository access", "commit records", "deliverables"],
      },
      {
        label: "Witness / meeting statements",
        signals: ["witness", "written statement", "signed statement", "affidavit", "meeting minutes", "testimony"],
      },
    ],
  },
  cyber_fraud_impersonation: {
    label: "Cyber Fraud / Impersonation",
    requirements: [
      {
        label: "Account security alerts / login notifications",
        signals: ["security alert", "login notification", "sign in alert", "account recovery", "password reset"],
      },
      {
        label: "Device, IP address / access logs",
        signals: ["device logs", "ip address", "access logs", "login history", "server logs"],
      },
      {
        label: "Phishing / impersonation messages or links",
        signals: ["phishing message", "impersonation message", "fake website", "fake account link", "spoofed email"],
      },
      {
        label: "Financial transaction records, if money was lost",
        signals: ["bank statement", "transaction receipt", "payment record", "utr", "transaction id"],
      },
    ],
  },
  financial: {
    label: "Financial / money fraud",
    requirements: [
      {
        label: "SMS bank debit alert",
        signals: ["debit alert", "debit sms", "bank sms", "sms from bank", "sms alert"],
      },
      {
        label: "UTR / transaction reference number",
        signals: ["utr", "transaction reference", "reference number", "transaction id", "txn id"],
      },
      {
        label: "UPI merchant handle",
        signals: ["upi id", "merchant handle", "vpa", "upi handle"],
      },
      {
        label: "Bank statement or payment receipt",
        signals: ["bank statement", "payment receipt", "transaction screenshot", "payment screenshot"],
      },
      {
        label: "Chat / call logs",
        signals: ["call log", "call recording", "call history", "chat log", "whatsapp chat", "chat screenshot"],
      },
    ],
  },
  harassment: {
    label: "Harassment / cyberstalking",
    requirements: [
      {
        label: "Screenshots of fake profiles",
        signals: ["fake profile", "profile screenshot", "screenshot of the profile", "impersonation account"],
      },
      {
        label: "Threatening chat threads",
        signals: ["threatening chat", "threat message", "threatening message", "message screenshot", "dm screenshot"],
      },
      {
        label: "Call timestamps / call logs",
        signals: ["call timestamp", "call log", "call history", "call recording", "phone call"],
      },
      {
        label: "Defamatory post links",
        signals: ["defamatory post", "post link", "post url", "instagram post", "facebook post", "social media post"],
      },
      {
        label: "Account handles / profile links",
        signals: ["username", "account handle", "profile handle", "account link", "profile link"],
      },
    ],
  },
  assault: {
    label: "Assault / physical injury",
    requirements: [
      {
        label: "Medical records / injury photographs",
        signals: ["medical report", "medical records", "hospital record", "injury photo", "injury photograph"],
      },
      {
        label: "Witness details or statements",
        signals: ["witness", "witness statement", "eyewitness"],
      },
      {
        label: "CCTV / video footage",
        signals: ["cctv", "camera footage", "video footage", "security footage"],
      },
      {
        label: "Incident time and location",
        signals: ["incident time", "incident location", "at the scene", "at the location"],
      },
    ],
  },
  theft: {
    label: "Theft / property offence",
    requirements: [
      {
        label: "Proof of ownership / purchase records",
        signals: ["proof of ownership", "purchase receipt", "purchase records", "ownership document"],
      },
      {
        label: "Property identifiers",
        signals: ["serial number", "imei", "vehicle registration", "identifying marks"],
      },
      {
        label: "CCTV / video footage",
        signals: ["cctv", "camera footage", "video footage", "security footage"],
      },
      {
        label: "Witness details or statements",
        signals: ["witness", "witness statement", "eyewitness"],
      },
    ],
  },
  general: {
    label: "General incident",
    requirements: [
      {
        label: "Incident time and location",
        signals: ["incident time", "incident location", "at the scene", "at the location"],
      },
      {
        label: "Witness details or statements",
        signals: ["witness", "witness statement", "eyewitness"],
      },
      {
        label: "Photos / video / CCTV",
        signals: ["photo", "photograph", "video footage", "cctv", "camera footage"],
      },
      {
        label: "Medical records, if relevant",
        signals: ["medical report", "medical records", "hospital record", "injury photo", "injury photograph"],
      },
    ],
  },
};

const categoryPatterns = {
  commercial_contract_fraud: /\b(?:commercial contract fraud|contract fraud|breach of contract|commercial fraud|business dispute|contract dispute|non[- ]delivery of (?:services|goods|code|work)|withheld source code|commercial|contractor|vendor|supplier)\b/i,
  cyber_fraud_impersonation: /\b(?:hack(?:ed|ing)?|unauthori[sz]ed access|account takeover|data breach|data leak|phishing|identity theft|cyber fraud|online fraud|impersonat\w*|personation|spoof(?:ed|ing) identity)\b/i,
  financial: /\b(?:fraud|scam|money|bank|upi|transaction|transfer|debit|payment|wallet|extortion|cyber\s*fraud)\b/i,
  harassment: /\b(?:harass(?:ment)?|stalk(?:ing)?|cyberstalk(?:ing)?|fake profile|impersonat\w*|defamat\w*|threatening online|unwanted messages?|blackmail|doxx?\w*)\b/i,
  assault: /\b(?:assault|hit|injur\w*|grievous hurt|fight|beaten|physical attack|violence)\b/i,
  theft: /\b(?:theft|stolen|robbery|snatched|burglary|property stolen)\b/i,
};

function normalize(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

export function classifyCrimeCategory(narrative) {
  const text = narrative.trim();
  if (!text) return null;

  const matches = Object.entries(categoryPatterns)
    .map(([category, pattern]) => ({
      category,
      score: [...text.matchAll(new RegExp(pattern.source, pattern.flags + "g"))].length,
    }))
    .filter(({ score }) => score > 0)
    .sort((left, right) => right.score - left.score);

  return matches[0]?.category || "general";
}

export function getEvidenceRequirements(category, narrative) {
  const definition = evidenceByCategory[category] || evidenceByCategory.general;
  const normalizedNarrative = normalize(narrative);

  return definition.requirements.map(({ label, signals }) => ({
    label,
    available: signals.some((signal) =>
      normalizedNarrative.includes(normalize(signal)),
    ),
  }));
}

export function getEvidenceCategoryLabel(category) {
  return evidenceByCategory[category]?.label || null;
}

export function extractBnsSections(responses) {
  const citations = new Set();
  const sectionPattern = /\b(?:sections?|secs?\.?|§)\s*((?:\d+[a-z]?(?:\(\d+\))?)(?:\s*(?:,|and|&)\s*\d+[a-z]?(?:\(\d+\))?)*)/gi;
  const sectionNumberPattern = /\d+[a-z]?(?:\(\d+\))?/gi;
  const bnsPattern = /\b(?:BNS|Bharatiya Nyaya Sanhita(?:,\s*2023)?)\b/i;

  for (const response of responses) {
    const sentences = response.split(/(?<=[.!?])\s+|\n+/);
    for (const sentence of sentences) {
      if (!bnsPattern.test(sentence)) continue;

      for (const match of sentence.matchAll(sectionPattern)) {
        for (const section of match[1].matchAll(sectionNumberPattern)) {
          citations.add(section[0]);
        }
      }
    }
  }

  return [...citations].sort((left, right) =>
    left.localeCompare(right, undefined, { numeric: true }),
  );
}
