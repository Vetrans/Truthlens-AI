def generate_summary(risk_items: list, positive_features: list, readability: dict) -> str:
    """
    Dynamically generates a professional legal executive summary
    based on the exact risk and positive features detected in the document.
    """
    critical_count = sum(1 for r in risk_items if r["severity"] == "Critical")
    high_count = sum(1 for r in risk_items if r["severity"] == "High")
    med_count = sum(1 for r in risk_items if r["severity"] == "Medium")
    low_count = sum(1 for r in risk_items if r["severity"] == "Low")
    
    risk_names = [r["name"] for r in risk_items]
    pos_names = [p["name"] for p in positive_features]
    
    # 1. Build Lead Section
    if critical_count > 0:
        lead = f"CRITICAL ALERT: This document contains {critical_count} critical and {high_count} high-severity risks that heavily favor the service provider. Accepting these terms places significant restrictions on your privacy, legal rights, and financial control."
    elif high_count > 0:
        lead = f"WARNING: We detected {high_count} high-severity and {med_count} medium-severity risks in this document. Several clauses limit your legal recourse and expand data collection permissions beyond basic service requirements."
    elif med_count > 0:
        lead = f"MODERATE: This contract is relatively standard but contains {med_count} moderate and {low_count} low-severity clauses. It is recommended to review billing and tracking options before proceeding."
    else:
        lead = "SAFE: No critical, high, or medium legal risk clauses were detected. The terms appear unusually balanced and user-friendly."
        
    # 2. Build Legal and Privacy Details Section
    details = []
    
    # Dispute resolution clauses
    if "Mandatory Arbitration" in risk_names or "Class Action Waiver" in risk_names:
        disputes = []
        if "Mandatory Arbitration" in risk_names:
            disputes.append("mandatory binding arbitration")
        if "Class Action Waiver" in risk_names:
            disputes.append("a class-action waiver")
        details.append(f"Crucially, you are agreeing to {' and '.join(disputes)}, meaning any dispute must be resolved out of court individually, stripping you of your right to a jury trial.")
        
    # Privacy & Data sharing clauses
    privacy_risks = [r for r in risk_items if r["category"] == "Privacy"]
    if privacy_risks:
        p_desc = [pr["name"].lower() for pr in privacy_risks[:3]]
        details.append(f"Regarding privacy, the service engages in {', '.join(p_desc)}. This indicates a high level of background tracking, third-party sharing, or biometric usage.")
        
    # Financial clauses
    financial_risks = [r for r in risk_items if r["category"] == "Financial"]
    if financial_risks:
        f_desc = [fr["name"].lower() for fr in financial_risks]
        details.append(f"Financially, be aware of {', '.join(f_desc)}, which means charges will renew automatically or payments are strictly non-refundable.")
        
    # User Control clauses
    user_control_risks = [r for r in risk_items if r["category"] == "User Control" or r["id"] == "terminate_without_notice"]
    if user_control_risks:
        details.append("For user control, the company reserves unilateral rights to change terms without prior notice or terminate your access instantly at their sole discretion.")

    # 3. Build Positive Protections Section
    positives = []
    if positive_features:
        positives.append(f"On the positive side, the document includes key user protections: {', '.join(pos_names[:3])}.")
        
    # 4. Build Readability Summary
    readability_summary = f"Readability analysis indicates the text is classified as '{readability['reading_difficulty']}', containing {readability['word_count']:,} words with an estimated reading time of {readability['reading_time_minutes']} minutes."

    # Combine sections into a professional formatted report summary
    summary_paragraphs = [lead]
    if details:
        summary_paragraphs.append(" ".join(details))
    if positives:
        summary_paragraphs.append(" ".join(positives))
    summary_paragraphs.append(readability_summary)
    
    return "\n\n".join(summary_paragraphs)

def generate_recommendations(risk_items: list) -> list[str]:
    """
    Extracts a list of actionable advice items based on the risks found.
    """
    recommendations = []
    
    if not risk_items:
        return ["No action required. The document is safe and balanced."]
        
    for item in risk_items:
        rec = item.get("recommendation")
        if rec and rec not in recommendations:
            recommendations.append(rec)
            
    # Add general fallback recommendations if few are present
    if len(recommendations) < 3:
        recommendations.append("Download a copy of these terms for your archives in case they are changed without notice.")
        recommendations.append("When registering, check all billing and privacy toggles to opt-out of optional data sharing.")
        
    return recommendations
