import re

def count_syllables_in_word(word: str) -> int:
    """
    A heuristic syllable counter for English words.
    """
    word = word.lower().strip()
    if not word:
        return 0
    # Remove all non-alphabetic characters
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 0
    
    vowels = "aeiouy"
    count = 0
    prev_char_is_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_is_vowel:
            count += 1
        prev_char_is_vowel = is_vowel
        
    # Subtract silent 'e' at the end, but not for 'ee' (like agree, free, employee)
    if word.endswith("e") and not word.endswith("ee"):
        count -= 1
    # Adjust for 'le' endings preceded by a consonant
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    # Subtract common silent suffixes
    if word.endswith("es") or word.endswith("ed"):
        if not (word.endswith("ted") or word.endswith("ded") or word.endswith("eed") or word.endswith("les") or word.endswith("ges")):
            count -= 1
            
    return max(1, count)

def calculate_readability(text: str) -> dict:
    """
    Calculates readability statistics for the given text.
    Returns:
        - flesch_reading_ease (float)
        - flesch_kincaid_grade (float)
        - gunning_fog (float)
        - smog_index (float)
        - word_count (int)
        - sentence_count (int)
        - reading_time_minutes (int)
        - reading_difficulty (str)
    """
    if not text.strip():
        return {
            "flesch_reading_ease": 100.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog": 0.0,
            "smog_index": 0.0,
            "word_count": 0,
            "sentence_count": 0,
            "reading_time_minutes": 0,
            "reading_difficulty": "No Content"
        }

    # Split sentences (standard legal texts can have abbreviations, so we check for spaces/newlines after periods)
    sentences = [s.strip() for s in re.split(r'[.!?]+(?=\s|\n|$)', text) if s.strip()]
    sentence_count = len(sentences)
    if sentence_count == 0:
        sentence_count = 1
        
    # Split words
    words = [w.strip() for w in re.split(r'\s+', text) if w.strip()]
    cleaned_words = []
    for w in words:
        cw = re.sub(r'[^a-zA-Z]', '', w)
        if cw:
            cleaned_words.append(cw)
            
    word_count = len(cleaned_words)
    if word_count == 0:
        word_count = 1
        
    total_syllables = sum(count_syllables_in_word(w) for w in cleaned_words)
    complex_words = sum(1 for w in cleaned_words if count_syllables_in_word(w) >= 3)
    
    # 1. Flesch Reading Ease
    asl = word_count / sentence_count
    asw = total_syllables / word_count
    flesch_reading_ease = 206.835 - (1.015 * asl) - (84.6 * asw)
    flesch_reading_ease = max(0.0, min(100.0, flesch_reading_ease))
    
    # 2. Flesch-Kincaid Grade Level
    flesch_kincaid_grade = (0.39 * asl) + (11.8 * asw) - 15.59
    flesch_kincaid_grade = max(0.0, flesch_kincaid_grade)
    
    # 3. Gunning Fog Index
    pcw = (complex_words / word_count) * 100
    gunning_fog = 0.4 * (asl + pcw)
    gunning_fog = max(0.0, gunning_fog)
    
    # 4. SMOG Index
    # Scale complex words if sentence count is low to avoid division issues or inaccurate scores
    scaled_complex_words = complex_words * (30 / sentence_count)
    smog_index = 1.0430 * (scaled_complex_words ** 0.5) + 3.1291
    smog_index = max(0.0, smog_index)
    
    # Estimated Reading Time (Average reading speed of 200 words per minute)
    reading_time_minutes = max(1, round(word_count / 200))
    
    # Determine difficulty level label
    if flesch_reading_ease >= 90:
        difficulty = "Very Easy (5th Grade)"
    elif flesch_reading_ease >= 80:
        difficulty = "Easy (6th Grade)"
    elif flesch_reading_ease >= 70:
        difficulty = "Fairly Easy (7th Grade)"
    elif flesch_reading_ease >= 60:
        difficulty = "Standard (8th-9th Grade)"
    elif flesch_reading_ease >= 50:
        difficulty = "Fairly Difficult (10th-12th Grade)"
    elif flesch_reading_ease >= 30:
        difficulty = "Difficult (College level)"
    else:
        difficulty = "Very Confusing (College Graduate)"
        
    return {
        "flesch_reading_ease": round(flesch_reading_ease, 2),
        "flesch_kincaid_grade": round(flesch_kincaid_grade, 2),
        "gunning_fog": round(gunning_fog, 2),
        "smog_index": round(smog_index, 2),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "reading_time_minutes": reading_time_minutes,
        "reading_difficulty": difficulty
    }
