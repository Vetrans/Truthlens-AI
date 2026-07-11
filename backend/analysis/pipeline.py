import re
from backend.utilities.text_extractor import clean_text
from backend.utilities.readability import calculate_readability
from backend.classifier.clause_classifier import classify_clause
from backend.risk_engine.risk_detector import detect_risks_and_positives
from backend.summarizer.doc_summarizer import generate_summary, generate_recommendations

def split_into_clauses(text: str) -> list[str]:
    """
    Splits text into clean paragraph blocks and then breaks paragraphs
    down into distinct sentences/clauses using abbreviation-merging logic.
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    clauses = []
    
    abbreviations = {
        "eg", "ie", "etc", "vs", "co", "ltd", "approx", "pm", "am", 
        "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
    }
    
    for para in paragraphs:
        # Split by sentence end punctuation followed by whitespace or end of line
        raw_splits = re.split(r'([.!?]+(?:\s+|\n|$))', para)
        
        temp_sentences = []
        current = ""
        
        for part in raw_splits:
            if not part:
                continue
            if re.match(r'^[.!?]+\s*$', part):
                current += part
                temp_sentences.append(current.strip())
                current = ""
            else:
                current = part
                
        if current.strip():
            temp_sentences.append(current.strip())
            
        # Merge sentences that were split on abbreviations
        merged_sentences = []
        skip_next = False
        
        for idx, sent in enumerate(temp_sentences):
            if skip_next:
                skip_next = False
                continue
                
            # Check the last word of this sentence (ignoring punctuation)
            words = [w for w in re.split(r'\W+', sent) if w]
            if words:
                last_word = words[-1].lower()
                if last_word in abbreviations and idx + 1 < len(temp_sentences):
                    # Merge with the next sentence
                    merged_sentences.append(sent + " " + temp_sentences[idx + 1])
                    skip_next = True
                    continue
                    
            merged_sentences.append(sent)
            
        for s in merged_sentences:
            if len(s) > 12:
                clauses.append(s)
                
    if not clauses and text.strip():
        clauses = [text.strip()]
        
    return clauses


def run_analysis_pipeline(raw_text: str) -> dict:
    """
    Executes the full document analysis pipeline:
    1. Clean text
    2. Split into clauses
    3. Classify clauses
    4. Detect risks and positive protections
    5. Calculate readability statistics
    6. Score transparency and overall weighted risk
    7. Generate executive summary and recommendations
    """
    # Step 1 & 2: Clean and extract clauses
    cleaned_text = clean_text(raw_text)
    clauses_text = split_into_clauses(cleaned_text)
    
    # Step 3: Classify each clause
    classified_clauses = []
    for clause in clauses_text:
        classification = classify_clause(clause)
        classified_clauses.append({
            "clause_text": clause,
            "subcategory": classification["subcategory"],
            "primary_category": classification["primary_category"],
            "confidence": classification["confidence"]
        })
        
    # Step 4, 5, 6, 7: Detect risks/positives and compute initial category scores
    analysis_results = detect_risks_and_positives(classified_clauses)
    
    risk_items = analysis_results["risk_items"]
    positive_features = analysis_results["positive_features"]
    category_scores = analysis_results["category_risks"]
    weights = analysis_results["weights"]
    
    # Step 8: Calculate Transparency score and final weighted scores
    readability_stats = calculate_readability(cleaned_text)
    
    # Calculate Transparency Risk Score based on Reading Ease (FRE) and average sentence length
    fre = readability_stats["flesch_reading_ease"]
    transparency_risk = (100.0 - fre) / 10.0  # 100 FRE = 0 risk, 0 FRE = 10 risk
    
    # Penalty for average sentence length greater than 25 words
    asl = readability_stats["word_count"] / max(1, readability_stats["sentence_count"])
    if asl > 25:
        transparency_risk += 1.5
        
    category_scores["Transparency"] = round(max(0.0, min(10.0, transparency_risk)), 1)
    
    # Calculate Overall Weighted Risk Score (0-10)
    overall_score = sum(category_scores[cat] * weights[cat] for cat in weights)
    overall_score = round(overall_score, 2)
    
    # Identify findings that need manual review (confidence < 70%)
    for item in risk_items:
        if item["confidence"] < 70.0:
            item["needs_review"] = True
        else:
            item["needs_review"] = False
            
    for item in positive_features:
        if item["confidence"] < 70.0:
            item["needs_review"] = True
        else:
            item["needs_review"] = False
            
    # Calculate overall pipeline confidence (average of all classification predictions)
    if classified_clauses:
        avg_confidence = sum(c["confidence"] for c in classified_clauses) / len(classified_clauses)
    else:
        avg_confidence = 100.0
    avg_confidence = round(avg_confidence, 1)

    # Step 9: Generate dynamic executive summary & recommendations
    summary = generate_summary(risk_items, positive_features, readability_stats)
    recommendations = generate_recommendations(risk_items)
    
    # Organize statistics for dashboard
    statistics = {
        "clause_count": len(clauses_text),
        "word_count": readability_stats["word_count"],
        "sentence_count": readability_stats["sentence_count"],
        "critical_risk_count": sum(1 for r in risk_items if r["severity"] == "Critical"),
        "high_risk_count": sum(1 for r in risk_items if r["severity"] == "High"),
        "medium_risk_count": sum(1 for r in risk_items if r["severity"] == "Medium"),
        "low_risk_count": sum(1 for r in risk_items if r["severity"] == "Low"),
        "positive_count": len(positive_features)
    }

    return {
        "overall_score": overall_score,
        "category_scores": category_scores,
        "summary": summary,
        "positive_features": positive_features,
        "negative_features": risk_items,  # Matching the API output structure requested: 'negative_features'
        "risk_items": risk_items,
        "recommendations": recommendations,
        "statistics": statistics,
        "readability": readability_stats,
        "confidence": avg_confidence
    }