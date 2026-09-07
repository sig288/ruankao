import re
from typing import List, Dict, Any, Tuple
from app.schemas.practice import RubricMatchResult

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Lowercase and remove excessive whitespace/punctuation
    cleaned = re.sub(r'[\s，。、；：！？,\.\?!:;\-_]+', '', text.lower())
    return cleaned

def grade_case_answer(user_answer: str, rubrics: List[Dict[str, Any]]) -> Tuple[float, float, List[RubricMatchResult]]:
    """
    Semi-automatic case question scoring based on rubric keywords.
    Returns: (earned_score, total_score, match_results)
    """
    if not rubrics:
        return 0.0, 0.0, []

    norm_user = normalize_text(user_answer)
    total_score = 0.0
    earned_score = 0.0
    results: List[RubricMatchResult] = []

    for item in rubrics:
        point = item.get("point", "采分点")
        max_score = float(item.get("score", 1.0))
        keywords = item.get("keywords", [])
        total_score += max_score

        matched = []
        missing = []

        if not keywords:
            # If no keywords specified, fallback to checking if any part of the point matches
            norm_point = normalize_text(point)
            if norm_point in norm_user:
                matched.append(point)
            else:
                missing.append(point)
        else:
            for kw in keywords:
                norm_kw = normalize_text(kw)
                if norm_kw and norm_kw in norm_user:
                    matched.append(kw)
                else:
                    missing.append(kw)

        # Hit logic: at least one keyword matched or 50% matched
        is_hit = False
        item_score = 0.0

        if keywords:
            ratio = len(matched) / len(keywords)
            if ratio >= 0.5 or (len(keywords) == 1 and len(matched) == 1):
                is_hit = True
                item_score = max_score
            elif len(matched) > 0:
                is_hit = True
                item_score = round(max_score * ratio, 1)
        else:
            if matched:
                is_hit = True
                item_score = max_score

        earned_score += item_score
        results.append(RubricMatchResult(
            point=point,
            max_score=max_score,
            earned_score=item_score,
            matched_keywords=matched,
            missing_keywords=missing,
            is_hit=is_hit
        ))

    return round(earned_score, 1), round(total_score, 1), results
