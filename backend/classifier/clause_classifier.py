import re

# Mapping subcategories to primary scoring categories
CATEGORY_MAP = {
    # Privacy
    "Data Collection": "Privacy",
    "Data Sharing": "Privacy",
    "Cookies & Tracking": "Privacy",
    "Advertising": "Privacy",
    "Biometric Data": "Privacy",
    "Camera & Microphone": "Privacy",
    "Location Tracking": "Privacy",
    "Contacts Access": "Privacy",
    "Data Retention": "Privacy",
    "International Transfers": "Privacy",
    "AI Training": "Privacy",
    
    # Financial
    "Billing & Fees": "Financial",
    "Subscription": "Financial",
    "Auto Renewal": "Financial",
    "Refunds": "Financial",
    
    # Legal Rights
    "Termination": "Legal Rights",
    "Warranty Disclaimer": "Legal Rights",
    "Arbitration": "Legal Rights",
    "Class Action Waiver": "Legal Rights",
    "Intellectual Property": "Legal Rights",
    "Licensing": "Legal Rights",
    "Content Ownership": "Legal Rights",
    "Government Requests": "Legal Rights",
    "Limit of Liability": "Legal Rights",
    "Indemnification": "Legal Rights",
    "Waiver of Rights": "Legal Rights",
    
    # Security
    "Security & Encryption": "Security",
    
    # User Control
    "User Data Deletion": "User Control",
    "Data Export": "User Control",
    "Opt-Out Options": "User Control",
    "Notice of Changes": "User Control",
    "Account Deletion": "User Control"
}

# Subcategory Keywords and Phrases
KEYWORDS = {
    "Auto Renewal": [
        "auto-renew", "automatic renewal", "automatically renew", "auto-recurring", 
        "renews automatically", "recurring basis", "subsequent terms", "automatic extension"
    ],
    "Arbitration": [
        "arbitration", "arbitrate", "dispute resolution", "binding arbitration", 
        "aaa", "jams", "arbitrator", "out-of-court", "federal arbitration act"
    ],
    "Class Action Waiver": [
        "class action", "class representative", "representative action", "consolidated action", 
        "waive any right to participate", "class member", "class-wide"
    ],
    "Refunds": [
        "refund", "refundable", "no refund", "all sales are final", "reimbursement", 
        "return policy", "chargeback"
    ],
    "Billing & Fees": [
        "billing", "invoice", "charge", "payment card", "credit card", "fees", "prices", 
        "transaction", "billing cycle", "payment method", "tax", "late fee"
    ],
    "Subscription": [
        "subscription", "recurring", "monthly plan", "annual plan", "membership fee", 
        "cancel subscription", "billing term"
    ],
    "Data Sharing": [
        "share", "sell", "transfer", "disclose", "third parties", "advertisers", "partners", 
        "affiliates", "vendors", "service providers", "marketing partners", "sell your personal"
    ],
    "Data Collection": [
        "collect", "gather", "information we compile", "log data", "device information", 
        "personal information", "ip address", "browser type", "collect information", "data we collect"
    ],
    "Cookies & Tracking": [
        "cookies", "beacons", "pixels", "tracking technologies", "browser storage", 
        "local storage", "web beacon", "clear gifs", "tracking pixel"
    ],
    "Advertising": [
        "advertising", "advertisement", "targeted ads", "behavioral advertising", 
        "promotional emails", "marketing messages", "third-party ads"
    ],
    "AI Training": [
        "ai training", "machine learning", "train our models", "artificial intelligence", 
        "large language model", "llm training", "generative ai", "improve our algorithms"
    ],
    "Biometric Data": [
        "biometric", "facial recognition", "fingerprint", "face print", "retina scan", 
        "voiceprint", "face recognition"
    ],
    "Camera & Microphone": [
        "camera", "microphone", "access your mic", "record audio", "video recording", 
        "record video", "access camera", "access microphone"
    ],
    "Location Tracking": [
        "location", "gps", "geolocation", "precise location", "tracking location", 
        "find your device", "background location", "location data"
    ],
    "Contacts Access": [
        "contacts", "address book", "phone book", "friends list", "invite contacts", 
        "access contacts"
    ],
    "Data Retention": [
        "retain", "retention", "how long we keep", "stored for", "retention period", 
        "keep your data", "store data for"
    ],
    "International Transfers": [
        "transfer globally", "international transfer", "outside the eu", "transfer across borders", 
        "cross-border", "transfer data to", "outside your country"
    ],
    "Government Requests": [
        "law enforcement", "subpoena", "government requests", "disclosure to authorities", 
        "legal process", "warrant", "court order"
    ],
    "Termination": [
        "terminate", "suspension", "close your account", "deactivate", "discontinue service", 
        "cancel service", "suspend access", "sole discretion to terminate"
    ],
    "Intellectual Property": [
        "intellectual property", "trademark", "patent", "copyright", "proprietary", 
        "trade secret", "infringement", "dmca"
    ],
    "Licensing": [
        "license to use", "grant us a", "royalty-free", "sublicensable", "perpetual license", 
        "irrevocable license", "worldwide license", "transferable license"
    ],
    "Content Ownership": [
        "your content", "you own", "ownership of content", "retain ownership", "user content", 
        "content you submit", "ownership rights"
    ],
    "Waiver of Rights": [
        "waive", "waiver", "give up the right", "relinquish", "voluntary waiver"
    ],
    "Limit of Liability": [
        "limit of liability", "consequential damages", "maximum liability", "not be liable", 
        "shall not exceed", "indirect damages", "limited to the amount paid", "incidental damages"
    ],
    "Indemnification": [
        "indemnify", "indemnification", "hold harmless", "defend and hold"
    ],
    "Warranty Disclaimer": [
        "warranty", "as is", "merchantability", "fitness for a particular purpose", 
        "no guarantee", "without warranties", "disclaims all warranties", "satisfactory quality"
    ],
    "Security & Encryption": [
        "encrypt", "encryption", "ssl", "tls", "security measures", "safeguard", 
        "unauthorized access", "breach", "data security", "administrative safeguards"
    ],
    "User Data Deletion": [
        "delete my data", "request deletion", "delete information", "right to erasure", 
        "erase my data", "remove my information"
    ],
    "Account Deletion": [
        "delete account", "close account", "terminate account", "cancel account"
    ],
    "Data Export": [
        "export data", "data portability", "download my data", "copy of your information", 
        "request a copy"
    ],
    "Opt-Out Options": [
        "opt-out", "opt out", "unsubscribe", "do not sell", "opt-out right"
    ],
    "Notice of Changes": [
        "notice before changes", "notify you of changes", "will notify you", "updates to these terms", 
        "amend these terms", "change terms"
    ]
}

def classify_clause(clause_text: str) -> dict:
    """
    Classifies a legal clause into a subcategory and primary category based on keyword density.
    Returns:
        - subcategory (str)
        - primary_category (str)
        - confidence (float)
        - keywords_matched (list)
    """
    clause_lower = clause_text.lower()
    
    # Store scores for each subcategory
    scores = {}
    matched_keywords_map = {}
    
    for subcat, keywords in KEYWORDS.items():
        matched = []
        for kw in keywords:
            # Check for substring match (case-insensitive)
            if kw in clause_lower:
                matched.append(kw)
        
        if matched:
            # Score is based on number of unique keywords matched
            # Give slightly more weight to matches of multi-word phrases
            score = sum(len(kw.split()) for kw in matched)
            scores[subcat] = score
            matched_keywords_map[subcat] = matched
            
    if not scores:
        return {
            "subcategory": "General Terms",
            "primary_category": "Other",
            "confidence": 50.0,
            "keywords_matched": []
        }
        
    # Pick subcategory with the highest score
    best_subcat = max(scores, key=scores.get)
    max_score = scores[best_subcat]
    
    # Confidence calculation: based on how strong the matches are
    # Max confidence is 95% for keyword matches, scaling down for fewer words matched.
    confidence = min(60.0 + (max_score * 10), 95.0)
    
    return {
        "subcategory": best_subcat,
        "primary_category": CATEGORY_MAP.get(best_subcat, "Other"),
        "confidence": round(confidence, 1),
        "keywords_matched": matched_keywords_map[best_subcat]
    }