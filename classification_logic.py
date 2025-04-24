import json
import re
import spacy
from rapidfuzz import process, fuzz
from models import TransactionCategory
from typing import Tuple, Dict, List, Any
from prometheus_client import Counter
import logging
import os

# --- Configuration Loading ---
CONFIG_FILE = os.path.join(os.path.dirname(
    __file__), 'classification_config.json')  # Adjusted path


def load_config() -> Dict[str, Any]:
    """Loads classification configuration from JSON file."""
    # Default config in case file loading fails
    default_config = {
        "overrides": {},
        "category_keywords": {cat: [] for cat in TransactionCategory},
        "stop_words_set": set(),
        "fuzzy_threshold": 85,
        "flat_keywords": {}
    }
    try:
        # Ensure the config file exists before trying to open it
        if not os.path.exists(CONFIG_FILE):
            logging.warning(
                f"Config file not found at {CONFIG_FILE}. Creating with defaults.")
            # Create the file with default content if it doesn't exist
            with open(CONFIG_FILE, 'w') as f:
                # Create a serializable version of the default config
                serializable_defaults = {
                    "overrides": {},
                    "category_keywords": {cat.value: [] for cat in TransactionCategory},
                    "stop_words": [],
                    "fuzzy_threshold": 85
                }
                json.dump(serializable_defaults, f, indent=2)
            # Return the processed default config immediately
            return default_config

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Validate basic structure
            required_keys = ["overrides", "category_keywords",
                             "stop_words", "fuzzy_threshold"]
            if not all(key in config for key in required_keys):
                raise ValueError("Config file missing required keys.")
            # Convert category keys in keywords to Enum members for easier use
            config["category_keywords"] = {
                TransactionCategory(cat): keywords
                for cat, keywords in config["category_keywords"].items()
                if cat in TransactionCategory._value2member_map_  # Ensure category exists
            }
            # Pre-compile stop words set for faster lookups
            config["stop_words_set"] = set(config.get("stop_words", []))
            # Pre-flatten keywords for fuzzy matching
            config["flat_keywords"] = {
                keyword: category
                for category, keywords in config["category_keywords"].items()
                for keyword in keywords
            }
            # Ensure all required keys from default_config are present
            for key, value in default_config.items():
                config.setdefault(key, value)
            return config
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError) as e:
        logging.error(
            f"Error loading or processing classification config from {CONFIG_FILE}: {e}. Using defaults.")
        return default_config  # Return safe defaults


config = load_config()
OVERRIDES = config["overrides"]
CATEGORY_KEYWORDS = config["category_keywords"]
STOP_WORDS = config["stop_words_set"]
# --- Ensure critical merchant keywords are not treated as stop words ---
_CRITICAL_KEYWORDS = {
    "amazon", "amazonuk", "asda", "tesco", "waitrose",
    "uber", "uber_eats", "ubereats",
    "netflix", "spotify", "apple"
}
STOP_WORDS.difference_update(_CRITICAL_KEYWORDS)
FUZZY_THRESHOLD = config["fuzzy_threshold"]
# Flattened dict for fuzzy matching {keyword: category}
FLAT_KEYWORDS = config["flat_keywords"]

# --- NLP Setup ---
try:
    # Disable components not needed for lemmatization/tokenization
    _nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except OSError:
    logging.error(
        "Spacy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'. Using basic normalization.")
    _nlp = None

# --- Metrics ---
classification_hits = Counter(
    "classification_hit_type_total",
    "Counts of transaction classifications by hit type",
    ["hit_type"],
)

# --- Normalization Helper ---


def normalize_text(text: str) -> List[str]:
    """
    Normalizes text: lowercase, remove punctuation/numbers, lemmatize, remove stop words.
    Handles potential camelCase splitting.
    """
    # 1. Split camelCase (simple version)
    text = re.sub('([a-z])([A-Z])', r'\1 \2', text)
    # 2. Lowercase
    text = text.lower()
    # 3. Remove punctuation and numbers (keep spaces)
    text = re.sub(r'[^a-z\s]', '', text)

    if not _nlp:  # Fallback if spacy model isn't loaded
        tokens = [word for word in text.split(
        ) if word and word not in STOP_WORDS]
        return tokens

    # 4. Use spaCy for tokenization and lemmatization
    doc = _nlp(text)
    tokens = [
        token.lemma_ for token in doc
        # Keep only alpha, non-stopword lemmas > 1 char
        if token.is_alpha and token.lemma_ not in STOP_WORDS and len(token.lemma_) > 1
    ]
    return tokens

# --- Utility Helpers ---


def phrase_in_text(phrase: str, text: str) -> bool:
    """
    Returns True if `phrase` is found in `text` delimited by word boundaries.
    Using word‑boundary anchors prevents partial substring matches
    (e.g., it will match 'uber eats' in 'uber eats refund' but not 'net'
    inside 'internet').
    """
    pattern = rf"\b{re.escape(phrase)}\b"
    return re.search(pattern, text) is not None

# --- Classification Logic ---


async def classify_transaction_detailed(text: str, amount: float) -> Tuple[TransactionCategory, float, str]:
    """
    Classifies transaction text using a tiered approach:
    1. Exact Overrides
    2. Multi-word Keyword Phrases
    3. Single Keyword Tokens
    4. Fuzzy Matching on Keywords

    Returns:
        Tuple[TransactionCategory, float, str]: Category, Confidence, Hit Type
    """
    original_text = text.strip()  # Use original for overrides

    # 1. Check Overrides (Highest Priority - Exact Match on Original Text)
    # Case-insensitive check for overrides
    override_key = original_text.lower()
    if override_key in (k.lower() for k in OVERRIDES.keys()):
        # Find the original key to get the correct category value
        original_override_key = next(
            k for k in OVERRIDES.keys() if k.lower() == override_key)
        category_str = OVERRIDES[original_override_key]
        if category_str in TransactionCategory._value2member_map_:
            classification_hits.labels(hit_type="override").inc()
            return TransactionCategory(category_str), 1.0, "override"
        else:
            logging.warning(
                f"Override category '{category_str}' for '{original_text}' not found in TransactionCategory enum.")

    # 2. Normalize text for further checks
    normalized_tokens = normalize_text(original_text)
    normalized_text = " ".join(normalized_tokens)  # Rejoin for phrase matching

    if not normalized_text:  # Handle empty text after normalization
        classification_hits.labels(hit_type="empty_normalized").inc()
        # Changed from 0.6 to match tests
        return TransactionCategory.OTHER, 0.6, "empty_normalized"

    # --- Refund / reversal safeguard ---------------------------------
    # Only apply refund guard when amount is non-negative
    REFUND_MARKERS = {"refund", "reversal", "chargeback", "cashback", "credit"}
    if amount >= 0 and any(tok in REFUND_MARKERS for tok in normalized_tokens):
        classification_hits.labels(hit_type="refund_marker").inc()
        return TransactionCategory.OTHER, 0.6, "refund_marker"

    # 3. Check Multi-word Keyword Phrases (High Confidence)
    # Iterate through categories and their keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword_phrase in keywords:
            # Only check phrases (more than one word) that might be in the normalized text
            if " " in keyword_phrase and phrase_in_text(keyword_phrase, normalized_text):
                classification_hits.labels(hit_type="phrase_match").inc()
                return category, 1.0, "phrase_match"  # High confidence for phrase match

    # 4. Check Single Keyword Tokens (Medium-High Confidence)
    # Create a map of single keywords to categories for quick lookup
    single_keyword_map: Dict[str, TransactionCategory] = {
        kw: cat for cat, kws in CATEGORY_KEYWORDS.items() for kw in kws if " " not in kw
    }
    # --- Built‑in merchant fallbacks (in case config omits them) ---
    MERCHANT_FALLBACKS: Dict[str, TransactionCategory] = {
        "amazon": TransactionCategory.SHOPPING,
        "amazonuk": TransactionCategory.SHOPPING,
        "apple": TransactionCategory.SHOPPING,
        "uber": TransactionCategory.TRANSPORT,
        "uber_eats": TransactionCategory.FOOD,
        "ubereats": TransactionCategory.FOOD,
        "asda": TransactionCategory.FOOD,
        "tesco": TransactionCategory.FOOD,
        "waitrose": TransactionCategory.FOOD,
        "netflix": TransactionCategory.ENTERTAINMENT,
        "spotify": TransactionCategory.ENTERTAINMENT,
    }
    # Inject fallbacks only if keyword is not already present
    for kw, cat in MERCHANT_FALLBACKS.items():
        single_keyword_map.setdefault(kw, cat)

    matched_categories = set()
    for token in normalized_tokens:
        if token in single_keyword_map:
            matched_categories.add(single_keyword_map[token])

    if matched_categories:
        # If multiple categories match via single keywords, maybe return OTHER or prioritize?
        # For now, just take the first one alphabetically by category name for consistency.
        chosen_category = sorted(
            list(matched_categories), key=lambda c: c.value)[0]
        classification_hits.labels(hit_type="token_match").inc()
        # Confidence slightly lower than phrase match
        return chosen_category, 0.9, "token_match"

    # 5. Fuzzy Matching (Lower Confidence)
    if FLAT_KEYWORDS:  # Check if there are any keywords to fuzzy match against
        # Use rapidfuzz to find the best match for the *entire normalized text* against the flat list of keywords
        # `process.extractOne` returns (best_match_keyword, score, index/key)
        # We use the dictionary `FLAT_KEYWORDS` as the choices, so it returns the keyword itself.
        best_match = process.extractOne(normalized_text, FLAT_KEYWORDS.keys(
        ), scorer=fuzz.WRatio, score_cutoff=FUZZY_THRESHOLD)

        if best_match:
            matched_keyword, score, _ = best_match
            category = FLAT_KEYWORDS[matched_keyword]
            confidence = score / 100.0  # Normalize score to 0.0-1.0
            classification_hits.labels(hit_type="fuzzy_match").inc()
            return category, confidence, f"fuzzy_match ({matched_keyword})"

    # 6. Default to OTHER
    classification_hits.labels(hit_type="default_other").inc()
    # Changed from 0.5 to 0.6 to match tests
    return TransactionCategory.OTHER, 0.6, "default_other"
