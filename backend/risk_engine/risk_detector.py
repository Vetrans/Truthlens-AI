import re

# Negative Risk Rules Definition
RISK_RULES = [
    {
        "id": "mandatory_arbitration",
        "name": "Mandatory Arbitration",
        "category": "Legal Rights",
        "severity": "High",
        "triggers": ["arbitrate", "arbitration", "binding arbitration", "dispute resolution by arbitration", "aaa", "jams"],
        "anti_triggers": ["no arbitration", "arbitration is optional", "do not require arbitration"],
        "explanation": "The company requires all legal disputes to be settled through binding arbitration rather than in court.",
        "why_it_matters": "This strips away your constitutional right to sue the company in court, have a trial by jury, or participate in collective legal actions.",
        "recommendation": "If an opt-out mechanism is available, submit your opt-out request in writing immediately (usually within 30 days of registration).",
        "plain_english": "You agree to resolve any legal disagreements out of court with a private arbitrator instead of suing in a normal court."
    },
    {
        "id": "class_action_waiver",
        "name": "Class Action Waiver",
        "category": "Legal Rights",
        "severity": "Critical",
        "triggers": ["class action", "representative action", "class representative", "class member", "waive any right to participate"],
        "anti_triggers": [],
        "explanation": "You waive your right to join other users in a collective or class action lawsuit against the company.",
        "why_it_matters": "Individual lawsuits are often financially impossible for small claims. By waiving class action rights, the company avoids accountability for widespread minor damages.",
        "recommendation": "Check if there is an opt-out window. If not, understand that any legal action you take must be done individually at your own expense.",
        "plain_english": "You give up your right to join other users to sue the company together as a group."
    },
    {
        "id": "change_terms_anytime",
        "name": "Can Change Terms Anytime",
        "category": "User Control",
        "severity": "High",
        "triggers": ["change", "modify", "amend", "update", "revise"],
        "trigger_combinations": [["at any time", "sole discretion"], ["without notice"], ["without prior notice"], ["without obligation to notify"]],
        "anti_triggers": ["notify you before", "give notice", "prior notice"],
        "explanation": "The company reserves the right to modify these terms at any time without notifying you directly.",
        "why_it_matters": "They can change pricing, privacy settings, or features without your knowledge. Your continued use of the service is deemed as automatic acceptance.",
        "recommendation": "Periodically check the 'last updated' date on the terms page or use web monitors to track changes.",
        "plain_english": "The company can change this contract whenever they want, and they don't have to warn you first."
    },
    {
        "id": "auto_renewal",
        "name": "Automatic Subscription Renewal",
        "category": "Financial",
        "severity": "Medium",
        "triggers": ["auto-renew", "automatic renewal", "automatically renew", "auto-recurring", "renews automatically", "recurring basis", "subsequent terms"],
        "anti_triggers": ["will not automatically renew", "non-recurring"],
        "explanation": "Your subscription will automatically renew at the end of the billing term, and you will be charged again.",
        "why_it_matters": "If you forget the renewal date, you will be billed for service you may no longer want or use.",
        "recommendation": "Disable auto-renewal in your billing settings immediately after subscribing, or set a calendar reminder 3 days before renewal.",
        "plain_english": "They will keep charging your card for subscription renewals unless you cancel in advance."
    },
    {
        "id": "no_refund",
        "name": "No Refund Policy",
        "category": "Financial",
        "severity": "Medium",
        "triggers": ["no refund", "non-refundable", "all sales are final", "no reimbursement", "no return", "fees are final"],
        "anti_triggers": ["refundable within", "money-back guarantee", "refund policy"],
        "explanation": "The company has a strict 'no refunds' policy for all purchases and subscriptions.",
        "why_it_matters": "If the service fails, gets shut down, or doesn't meet your expectations, you cannot recover your money.",
        "recommendation": "Try the service using a free trial or monthly subscription first before committing to an expensive annual plan.",
        "plain_english": "Once you pay them, you cannot get your money back under any circumstances."
    },
    {
        "id": "share_third_parties",
        "name": "Share Data With Third Parties",
        "category": "Privacy",
        "severity": "High",
        "triggers": ["share", "disclose", "transfer"],
        "trigger_combinations": [["third parties"], ["partners", "affiliates"], ["advertisers"], ["marketing partners"]],
        "anti_triggers": ["do not share", "never sell or share", "do not disclose to third parties"],
        "explanation": "The company shares your personal data and usage details with third-party partners, affiliates, or advertisers.",
        "why_it_matters": "Your data is distributed outside the primary service, increasing the risk of data leaks and targeted tracking by advertising networks.",
        "recommendation": "Go to settings to toggle off 'third-party sharing' or opt-out of interest-based ads if possible.",
        "plain_english": "The company gives or sells your personal information to other companies."
    },
    {
        "id": "collect_biometrics",
        "name": "Collect Biometric Data",
        "category": "Privacy",
        "severity": "Critical",
        "triggers": ["biometric", "facial recognition", "fingerprint", "face print", "retina scan", "voiceprint", "face recognition"],
        "anti_triggers": [],
        "explanation": "The service collects and processes highly sensitive biometric data like faceprints or fingerprints.",
        "why_it_matters": "Unlike passwords, biometric data cannot be changed. If compromised, it creates a permanent identity theft risk.",
        "recommendation": "Disable biometric logins if optional. Carefully evaluate whether you trust this service with unchangeable physical identifiers.",
        "plain_english": "They collect your unique physical characteristics like your face, fingerprints, or voice."
    },
    {
        "id": "collect_gps",
        "name": "Collect GPS Location Data",
        "category": "Privacy",
        "severity": "High",
        "triggers": ["gps", "geolocation", "precise location", "tracking location", "background location", "location data"],
        "anti_triggers": ["do not track location", "never collect location"],
        "explanation": "The app tracks and stores your precise geographical coordinates, even in the background.",
        "why_it_matters": "This allows the company to build a detailed diary of your physical movements, home/work locations, and habits.",
        "recommendation": "Turn off location permissions in your phone's operating system settings, or set it to 'Only While Using App'.",
        "plain_english": "They track exactly where you are in the physical world using your device's GPS."
    },
    {
        "id": "collect_contacts",
        "name": "Access Contacts & Address Book",
        "category": "Privacy",
        "severity": "Medium",
        "triggers": ["contacts", "address book", "phone book", "friends list", "access contacts"],
        "anti_triggers": [],
        "explanation": "The service requests access to your device's contact list and uploads it to their servers.",
        "why_it_matters": "This violates the privacy of your friends and family, whose phone numbers and emails are shared without their consent.",
        "recommendation": "Deny contact list access when prompted by the app. Enter friend invites manually instead.",
        "plain_english": "They copy and upload all the phone numbers and email addresses stored on your phone."
    },
    {
        "id": "track_usage",
        "name": "Track Usage & Analytics",
        "category": "Privacy",
        "severity": "Low",
        "triggers": ["track usage", "analytics", "tracking cookies", "cookies and beacons", "activity tracking", "monitor your activity"],
        "anti_triggers": ["do not track", "no tracking"],
        "explanation": "The system tracks your detailed behavior, clicks, page views, and interactions within the app.",
        "why_it_matters": "It creates a granular behavioral profile of your online activities to build advertising segments.",
        "recommendation": "Use browser extensions like adblockers or privacy protection filters (e.g. uBlock Origin) and enable 'Do Not Track'.",
        "plain_english": "They watch and record everything you click on and read while using their app."
    },
    {
        "id": "unlimited_license",
        "name": "Unlimited & Perpetual License to Your Content",
        "category": "Legal Rights",
        "severity": "High",
        "triggers": ["royalty-free", "sublicensable", "perpetual license", "irrevocable license", "worldwide license", "transferable license", "grant us a license"],
        "anti_triggers": [],
        "explanation": "You grant the company an irrevocable, worldwide, perpetual, royalty-free license to use, edit, and distribute your content.",
        "why_it_matters": "Even if you delete your account or content, the company can legally keep using, selling, or displaying your creations forever without paying you.",
        "recommendation": "Be cautious about uploading valuable original work, art, or private writing to this service.",
        "plain_english": "You permanently give the company free permission to do whatever they want with the content you post."
    },
    {
        "id": "sell_data",
        "name": "Sell Personal Data",
        "category": "Privacy",
        "severity": "Critical",
        "triggers": ["sell your personal", "sell data", "commercialize your information", "monetize user data"],
        "anti_triggers": ["do not sell", "never sell your", "we do not sell"],
        "explanation": "The company explicitly states they may sell or monetize your personal information to third parties.",
        "why_it_matters": "Your private data is treated as a commodity, resulting in spam, unsolicited calls, and leaks to data brokers.",
        "recommendation": "Under CCPA/GDPR, immediately submit a 'Do Not Sell My Info' request via the link on their website.",
        "plain_english": "They sell your private information to marketing firms and data brokers for money."
    },
    {
        "id": "ai_training",
        "name": "AI Model Training on User Content",
        "category": "Privacy",
        "severity": "Medium",
        "triggers": ["ai training", "train our models", "machine learning training", "large language model", "llm training", "generative ai training"],
        "anti_triggers": ["do not use your content for ai", "opt-out of ai training"],
        "explanation": "The company uses your uploaded content, images, or texts to train their artificial intelligence models.",
        "why_it_matters": "Your creative works and writings are absorbed into commercial datasets, potentially generating derivatives without credit or payment.",
        "recommendation": "If available, toggle off 'AI Model Training' in settings, or avoid uploading high-value proprietary works.",
        "plain_english": "They use your private files and posts to train their artificial intelligence systems."
    },
    {
        "id": "terminate_without_notice",
        "name": "Account Termination Without Notice",
        "category": "Legal Rights",
        "severity": "High",
        "triggers": ["terminate at any time", "suspend access without notice", "sole discretion to terminate", "without warning", "without prior notice"],
        "anti_triggers": ["give 30 days notice", "provide written warning"],
        "explanation": "The company can suspend or permanently terminate your account at any time, for any reason, without warning.",
        "why_it_matters": "You could lose access to all your files, purchases, data, and settings instantly, with no right to appeal.",
        "recommendation": "Maintain independent backups of all critical files and data stored on this platform.",
        "plain_english": "They can ban you and delete your account whenever they want, for no reason, without warning."
    },
    {
        "id": "limit_liability",
        "name": "Severe Limitation of Liability",
        "category": "Legal Rights",
        "severity": "Medium",
        "triggers": ["limit of liability", "consequential damages", "maximum liability", "not be liable", "shall not exceed", "indirect damages", "limited to the amount paid"],
        "anti_triggers": [],
        "explanation": "The company severely limits the financial damages you can claim if their software or service causes you harm.",
        "why_it_matters": "Even if the company's negligence causes you major financial loss, data breach, or business disruption, you cannot recover full damages.",
        "recommendation": "Use this service only for tasks where a failure will not lead to catastrophic financial or physical consequences.",
        "plain_english": "If the app breaks and costs you money, the maximum they will pay you is very small (often $0 or what you paid them)."
    },
    {
        "id": "indemnification",
        "name": "Broad User Indemnification",
        "category": "Legal Rights",
        "severity": "High",
        "triggers": ["indemnify", "indemnification", "hold harmless", "defend and hold"],
        "anti_triggers": [],
        "explanation": "You agree to pay the legal fees and damages if the company gets sued because of something you did.",
        "why_it_matters": "You could face massive legal expenses if a third party sues the company over content you posted, even if it was accidental.",
        "recommendation": "Avoid posting copyrighted material, defamatory statements, or violating security rules that could trigger lawsuits.",
        "plain_english": "If the company gets sued because of your actions, you have to pay all of their legal bills and damages."
    },
    {
        "id": "waiver_of_rights",
        "name": "Waiver of Statutory Rights",
        "category": "Legal Rights",
        "severity": "Medium",
        "triggers": ["waive", "waiver", "give up the right", "relinquish", "voluntary waiver"],
        "anti_triggers": [],
        "explanation": "You are asked to waive specific legal protections or rights granted to you by consumer protection laws.",
        "why_it_matters": "It weakens your standing in legal disputes and gives up safety nets designed to protect consumers from unfair contracts.",
        "recommendation": "Be aware that local consumer protection laws sometimes override illegal waivers. Consult a legal expert if a dispute arises.",
        "plain_english": "You agree to give up certain legal rights that are normally guaranteed to you by law."
    }
]

# Positive Protection Rules Definition
POSITIVE_RULES = [
    {
        "id": "gdpr_compliance",
        "name": "GDPR Compliance",
        "category": "User Control",
        "severity": "High",
        "triggers": ["gdpr", "general data protection regulation", "european union", "right to erasure", "data portability"],
        "anti_triggers": [],
        "explanation": "The company complies with GDPR standards, offering strong privacy protections.",
        "why_it_matters": "This guarantees EU users (and often global users) the right to access, correct, delete, and restrict their personal data.",
        "recommendation": "Utilize the GDPR privacy request dashboard to audit and download the personal data they hold.",
        "plain_english": "They follow strict European privacy laws, which gives you maximum control over your personal data."
    },
    {
        "id": "ccpa_compliance",
        "name": "CCPA/CPRA Compliance",
        "category": "User Control",
        "severity": "High",
        "triggers": ["ccpa", "cpra", "california consumer", "california privacy"],
        "anti_triggers": [],
        "explanation": "The company complies with California Consumer Privacy Act standards.",
        "why_it_matters": "It gives you the right to opt-out of data sales, know what data is collected, and request deletion.",
        "recommendation": "Click the 'Do Not Sell My Info' link at the bottom of their site if you want to restrict data sharing.",
        "plain_english": "They follow California's privacy laws, allowing you to stop them from selling your data."
    },
    {
        "id": "encryption",
        "name": "Data Encryption Safeguards",
        "category": "Security",
        "severity": "High",
        "triggers": ["encrypt", "encryption", "ssl", "tls", "aes-256", "securely transmit", "cryptographic hash"],
        "anti_triggers": ["no encryption"],
        "explanation": "The service encrypts your data both in transit and at rest.",
        "why_it_matters": "It prevents hackers and unauthorized parties from reading your files, passwords, or personal details if intercepted.",
        "recommendation": "Ensure your browser shows a lock icon (HTTPS) when interacting with the service.",
        "plain_english": "They scramble your files and data so only authorized users can read them."
    },
    {
        "id": "user_can_delete_data",
        "name": "User Right to Delete Data",
        "category": "User Control",
        "severity": "High",
        "triggers": ["delete your data", "request deletion", "erase my data", "remove your information", "delete account at any time"],
        "anti_triggers": ["cannot delete", "data is retained permanently"],
        "explanation": "You have the right to request deletion of all your personal data from their servers.",
        "why_it_matters": "This allows you to erase your digital footprint from their platform completely when you stop using it.",
        "recommendation": "Submit a deletion request through your account settings if you decide to close your account.",
        "plain_english": "You can ask them to delete all of your personal files and info, and they must comply."
    },
    {
        "id": "data_export",
        "name": "Data Portability & Export",
        "category": "User Control",
        "severity": "Medium",
        "triggers": ["export data", "download my data", "data portability", "copy of your information", "request a copy"],
        "anti_triggers": [],
        "explanation": "The platform allows you to export and download all your uploaded content and personal data.",
        "why_it_matters": "You are not locked into their system. You can easily back up your files or migrate them to a competitor.",
        "recommendation": "Regularly download a copy of your account data for archival purposes.",
        "plain_english": "You can download a full backup copy of all your files and account data at any time."
    },
    {
        "id": "refund_policy",
        "name": "Fair Refund Policy",
        "category": "Financial",
        "severity": "High",
        "triggers": ["refundable within", "money-back guarantee", "refund policy", "full refund within"],
        "anti_triggers": ["no refund", "non-refundable"],
        "explanation": "The service offers a clear refund policy or a money-back guarantee period (e.g. 14 or 30 days).",
        "why_it_matters": "It reduces the financial risk of trying the service, allowing you to cancel and get your money back if it's not a fit.",
        "recommendation": "Note the exact deadline of the refund window when you purchase.",
        "plain_english": "You can cancel your subscription within a certain period and get a full refund."
    },
    {
        "id": "notice_before_changes",
        "name": "Prior Notice Before Changing Terms",
        "category": "User Control",
        "severity": "High",
        "triggers": ["notify you before", "give notice", "prior notice", "30 days notice", "notice of material changes"],
        "anti_triggers": ["without notice", "change at any time without"],
        "explanation": "The company promises to notify you in advance before changing contract terms or policies.",
        "why_it_matters": "This gives you time to review the changes and opt-out or close your account if you disagree with the new terms.",
        "recommendation": "Read email updates from the service regarding terms modifications.",
        "plain_english": "They will warn you in advance before they make any changes to this agreement."
    },
    {
        "id": "user_owns_content",
        "name": "User Ownership of Content",
        "category": "Legal Rights",
        "severity": "High",
        "triggers": ["you own", "ownership of content", "retain ownership", "content you submit is yours", "keep ownership"],
        "anti_triggers": ["transfer ownership to us", "we own your content"],
        "explanation": "The terms explicitly state that you retain complete copyright and ownership over everything you post or upload.",
        "why_it_matters": "You don't have to worry about the company stealing your creative projects, files, or writing to monetize them separately.",
        "recommendation": "Review license grants to ensure they are limited to 'displaying the service' rather than commercial distribution.",
        "plain_english": "You keep full ownership and copyrights of everything you upload or write in the app."
    }
]

def check_combination_triggers(text: str, combinations: list[list[str]]) -> bool:
    text_lower = text.lower()
    for combo in combinations:
        if all(term in text_lower for term in combo):
            return True
    return False

def detect_risks_and_positives(classified_clauses: list[dict]) -> dict:
    """
    Evaluates classified clauses to detect specific risks and positive protections.
    Returns:
        - overall_score (float, 0-10)
        - category_scores (dict)
        - risk_items (list)
        - positive_features (list)
    """
    risk_items = []
    positive_features = []
    
    # Track which rule IDs have already been triggered to avoid duplicate warnings
    triggered_rules = set()
    
    for c in classified_clauses:
        clause_text = c["clause_text"]
        clause_lower = clause_text.lower()
        subcat = c["subcategory"]
        
        # 1. Evaluate Negative Risks
        for rule in RISK_RULES:
            if rule["id"] in triggered_rules:
                continue
                
            # Basic triggers
            matches_trigger = any(trigger in clause_lower for trigger in rule["triggers"])
            
            # Check combinations if defined
            if "trigger_combinations" in rule:
                matches_trigger = matches_trigger or check_combination_triggers(clause_text, rule["trigger_combinations"])
                
            # If triggered, check anti-triggers
            if matches_trigger:
                matches_anti = any(anti in clause_lower for anti in rule["anti_triggers"])
                if not matches_anti:
                    triggered_rules.add(rule["id"])
                    risk_items.append({
                        "id": rule["id"],
                        "name": rule["name"],
                        "category": rule["category"],
                        "severity": rule["severity"],
                        "confidence": c["confidence"],
                        "explanation": rule["explanation"],
                        "why_it_matters": rule["why_it_matters"],
                        "recommendation": rule["recommendation"],
                        "plain_english": rule["plain_english"],
                        "original_clause": clause_text
                    })
                    
        # 2. Evaluate Positive Protections
        for rule in POSITIVE_RULES:
            if rule["id"] in triggered_rules:
                continue
                
            matches_trigger = any(trigger in clause_lower for trigger in rule["triggers"])
            
            if matches_trigger:
                matches_anti = any(anti in clause_lower for anti in rule["anti_triggers"])
                if not matches_anti:
                    triggered_rules.add(rule["id"])
                    positive_features.append({
                        "id": rule["id"],
                        "name": rule["name"],
                        "category": rule["category"],
                        "severity": rule["severity"],
                        "confidence": c["confidence"],
                        "explanation": rule["explanation"],
                        "why_it_matters": rule["why_it_matters"],
                        "recommendation": rule["recommendation"],
                        "plain_english": rule["plain_english"],
                        "original_clause": clause_text
                    })

    # 3. Calculate Explainable Weighted Scoring
    # Base risk score starts at 0.0 (no risks detected)
    category_risks = {
        "Privacy": 0.0,
        "Financial": 0.0,
        "Legal Rights": 0.0,
        "User Control": 0.0,
        "Security": 0.0
    }
    
    # Weights defined in requirements
    weights = {
        "Privacy": 0.25,
        "Financial": 0.20,
        "Legal Rights": 0.20,
        "User Control": 0.15,
        "Security": 0.10,
        "Transparency": 0.10
    }

    # Add points for Negative Risks
    for item in risk_items:
        cat = item["category"]
        if cat in category_risks:
            sev = item["severity"]
            if sev == "Low":
                category_risks[cat] += 1.0
            elif sev == "Medium":
                category_risks[cat] += 2.5
            elif sev == "High":
                category_risks[cat] += 4.0
            elif sev == "Critical":
                category_risks[cat] += 6.0
                
    # Subtract points for Positive Protections
    for item in positive_features:
        cat = item["category"]
        if cat in category_risks:
            sev = item["severity"]
            if sev == "Low":
                category_risks[cat] -= 1.0
            elif sev == "Medium":
                category_risks[cat] -= 1.5
            elif sev == "High" or sev == "Critical":
                category_risks[cat] -= 2.5

    # Ensure all category risk scores are bounded [0.0, 10.0]
    for cat in category_risks:
        category_risks[cat] = max(0.0, min(10.0, category_risks[cat]))

    # Transparency Score is calculated outside or inside this function.
    # Let's keep a placeholder inside and we will populate it in the pipeline or here.
    category_risks["Transparency"] = 0.0 # Will be populated based on readability statistics

    return {
        "category_risks": category_risks,
        "weights": weights,
        "risk_items": risk_items,
        "positive_features": positive_features
    }
