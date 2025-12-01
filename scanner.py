import re
from pydantic import BaseModel
from typing import Optional, List

# --- 1. Define Data Models ---
class Finding(BaseModel):
    """Represents a potential security violation found by Regex."""
    pattern_type: str       # e.g., "AWS_KEY", "CREDIT_CARD"
    matched_string: str     # The actual sensitive string found
    full_text: str          # The complete message context
    message_id: str         # ID to track back to the source

# --- 2. Define The Patterns ---
# We use standard Regex for common leaks
PATTERNS = {
    "AWS_ACCESS_KEY": r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])",  # Broad AWS Key pattern (20 chars caps)
    "AWS_SECRET_KEY": r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])", # 40 chars
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b", # Simple 13-16 digit matcher
    "STRIPE_TEST_KEY": r"sk_test_[0-9a-zA-Z]{24}" # Specific Stripe Test key
}

# --- 3. The Scanning Logic ---
def scan_message(message_obj: dict) -> List[Finding]:
    """
    Scans a single message dictionary for all defined patterns.
    Returns a list of 'Finding' objects (empty if safe).
    """
    findings = []
    text = message_obj.get("text", "")
    msg_id = message_obj.get("id", "unknown")

    for label, regex in PATTERNS.items():
        # Search for the pattern in the text
        matches = re.finditer(regex, text)
        
        for match in matches:
            matched_str = match.group()
            
            # Simple clean up (remove spaces from credit cards for cleaner logging)
            if label == "CREDIT_CARD":
                clean_match = matched_str.replace(" ", "").replace("-", "")
                if len(clean_match) < 13: continue # Too short after cleaning
            
            # Create the finding object
            finding = Finding(
                pattern_type=label,
                matched_string=matched_str,
                full_text=text,
                message_id=msg_id
            )
            findings.append(finding)

    return findings
