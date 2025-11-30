"""
Patient Search Utilities
Query type detection, phone normalization, fuzzy matching, and relevance scoring.
"""
import re
from enum import Enum
from typing import List, Dict, Tuple, Optional


class QueryType(Enum):
    """Types of search queries based on input pattern."""
    PATIENT_ID = "patient_id"   # Alphanumeric matching ID format
    PHONE = "phone"             # Digits only (3+ digits)
    NAME = "name"               # Letters and spaces only
    MIXED = "mixed"             # Alphanumeric (search ID + name)


def detect_query_type(query: str) -> QueryType:
    """
    Detect the type of search query based on content patterns.
    
    Args:
        query: The search query string
        
    Returns:
        QueryType enum indicating the detected type
    """
    if not query or len(query.strip()) < 2:
        return QueryType.NAME
    
    cleaned = query.strip()
    
    # Check if query is digits only (phone number pattern)
    digits_only = re.sub(r'[\s\-\(\)\+]', '', cleaned)
    if digits_only.isdigit() and len(digits_only) >= 3:
        return QueryType.PHONE
    
    # Check if query is letters and spaces only (name pattern)
    if re.match(r'^[a-zA-Z\s]+$', cleaned):
        return QueryType.NAME
    
    # Check if query matches patient ID format (alphanumeric, typically starts with P)
    if re.match(r'^[A-Za-z0-9]+$', cleaned) and len(cleaned) >= 4:
        # If it looks like a patient ID format (e.g., P20241234, PAT001)
        if cleaned[0].upper() == 'P' or len(cleaned) == 6:
            return QueryType.PATIENT_ID
        return QueryType.MIXED
    
    # Default to mixed for alphanumeric queries
    if re.match(r'^[a-zA-Z0-9\s]+$', cleaned):
        return QueryType.MIXED
    
    return QueryType.NAME


def normalize_phone(phone: str) -> str:
    """
    Remove formatting characters from phone numbers.
    Strips spaces, dashes, parentheses, and plus signs.
    
    Args:
        phone: Phone number string with potential formatting
        
    Returns:
        Normalized phone string with only digits
    """
    if not phone:
        return ""
    return re.sub(r'[\s\-\(\)\+\.]', '', phone)



def fuzzy_match(query: str, target: str, threshold: float = 0.6) -> Tuple[bool, float]:
    """
    Check if query fuzzy-matches target string using character-based similarity.
    
    Args:
        query: Search query string
        target: Target string to match against
        threshold: Minimum similarity score (0.0 to 1.0) for a match
        
    Returns:
        Tuple of (is_match, similarity_score)
    """
    if not query or not target:
        return False, 0.0
    
    query_lower = query.lower()
    target_lower = target.lower()
    
    # Exact substring match
    if query_lower in target_lower:
        return True, 1.0
    
    # Calculate Levenshtein-like similarity
    similarity = calculate_similarity(query_lower, target_lower)
    
    return similarity >= threshold, similarity


def calculate_similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity between two strings using a simple algorithm.
    Based on longest common subsequence ratio.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not s1 or not s2:
        return 0.0
    
    if s1 == s2:
        return 1.0
    
    # Check for substring match
    if s1 in s2 or s2 in s1:
        return len(min(s1, s2, key=len)) / len(max(s1, s2, key=len))
    
    # Calculate longest common subsequence
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    lcs_length = dp[m][n]
    return (2.0 * lcs_length) / (m + n)


def calculate_relevance(
    patient_id: str,
    full_name: str,
    phone: str,
    query: str,
    query_type: QueryType
) -> Tuple[float, str, List[Dict[str, int]]]:
    """
    Calculate relevance score for a patient based on query match.
    
    Args:
        patient_id: Patient's ID string
        full_name: Patient's full name
        phone: Patient's phone number
        query: Search query
        query_type: Detected query type
        
    Returns:
        Tuple of (relevance_score, match_field, match_positions)
    """
    query_lower = query.lower().strip()
    best_score = 0.0
    match_field = "name"
    match_positions: List[Dict[str, int]] = []
    
    # Check patient ID match (highest priority for exact match)
    if patient_id:
        patient_id_lower = patient_id.lower()
        if patient_id_lower == query_lower:
            return 1.0, "patient_id", [{"start": 0, "end": len(patient_id)}]
        elif query_lower in patient_id_lower:
            pos = patient_id_lower.find(query_lower)
            score = 0.9 * (len(query) / len(patient_id))
            if score > best_score:
                best_score = score
                match_field = "patient_id"
                match_positions = [{"start": pos, "end": pos + len(query)}]
    
    # Check name match
    if full_name:
        name_lower = full_name.lower()
        if query_lower in name_lower:
            pos = name_lower.find(query_lower)
            # Score based on match position and length
            position_bonus = 0.1 if pos == 0 else 0.0
            score = 0.8 * (len(query) / len(full_name)) + position_bonus
            if score > best_score:
                best_score = score
                match_field = "name"
                match_positions = [{"start": pos, "end": pos + len(query)}]
        else:
            # Try fuzzy match for names
            is_match, similarity = fuzzy_match(query, full_name)
            if is_match and similarity * 0.7 > best_score:
                best_score = similarity * 0.7
                match_field = "name"
                match_positions = []  # No exact positions for fuzzy match
    
    # Check phone match
    if phone and query_type in [QueryType.PHONE, QueryType.MIXED]:
        normalized_phone = normalize_phone(phone)
        normalized_query = normalize_phone(query)
        if normalized_query and normalized_query in normalized_phone:
            pos = normalized_phone.find(normalized_query)
            score = 0.85 * (len(normalized_query) / len(normalized_phone))
            if score > best_score:
                best_score = score
                match_field = "phone"
                # Find position in original phone string
                match_positions = find_phone_match_positions(phone, query)
    
    return best_score, match_field, match_positions


def find_phone_match_positions(phone: str, query: str) -> List[Dict[str, int]]:
    """Find match positions in phone string accounting for formatting."""
    if not phone or not query:
        return []
    
    normalized_query = normalize_phone(query)
    positions = []
    
    # Map normalized positions back to original
    norm_idx = 0
    start_idx = None
    matched_chars = 0
    
    for i, char in enumerate(phone):
        if char in '0123456789':
            if norm_idx < len(normalized_query) and char == normalized_query[norm_idx]:
                if start_idx is None:
                    start_idx = i
                matched_chars += 1
                norm_idx += 1
                if matched_chars == len(normalized_query):
                    positions.append({"start": start_idx, "end": i + 1})
                    break
            else:
                start_idx = None
                matched_chars = 0
                norm_idx = 0
    
    return positions


def find_match_positions(text: str, query: str) -> List[Dict[str, int]]:
    """
    Find all positions where query matches in text (case-insensitive).
    
    Args:
        text: Text to search in
        query: Query to find
        
    Returns:
        List of position dictionaries with start and end indices
    """
    if not text or not query:
        return []
    
    positions = []
    text_lower = text.lower()
    query_lower = query.lower()
    
    start = 0
    while True:
        pos = text_lower.find(query_lower, start)
        if pos == -1:
            break
        positions.append({"start": pos, "end": pos + len(query)})
        start = pos + 1
    
    return positions
