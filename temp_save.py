import os
import google.generativeai as genai
from dotenv import load_dotenv
from scanner import Finding

# --- 1. Setup and API Key Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Gemini API key setup complete.")
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
else:
    print(
        "🔑 Authentication Error: Please make sure you have a .env file in your project root "
        "with your 'GOOGLE_API_KEY' defined in it."
    )
    model = None # Set model to None if API key is missing

# --- 2. The "Brain" and "Coach" Logic ---

VERIFICATION_PROMPT_TEMPLATE = """
You are a security expert AI. A piece of text was flagged by a basic pattern scanner.
Your task is to determine if the flagged text is a real, live secret or just test data/documentation.

Context: The following message was found in an internal communication channel.
Message: "{full_text}"

The scanner flagged it for: {pattern_type}
The matched string was: "{matched_string}"

Analyze the message and the flagged content. Is this a real, sensitive credential or PII?
Answer with only "REAL" or "TEST".
"""

COACHING_PROMPT_TEMPLATE = """
You are PrivacyPal, a helpful security coach.
Your goal is to write a private, friendly message to a user who may have leaked data.
Do not shame them. Explain the risk simply and ask them to remediate the issue (e.g., "delete the message and rotate the credential").

The user '{user}' posted the following message:
"{full_text}"

This was flagged as a REAL risk because it appears to contain a "{pattern_type}".

Draft a brief, empathetic, and clear message to send privately to '{user}'.
"""

def verify_finding(finding: Finding) -> dict:
    """
    Uses Gemini to verify if a flagged message contains a real secret.
    Returns a dictionary with the verdict.
    """
    if not model:
        print("Cannot verify finding, Gemini model not configured.")
        return {"is_real_risk": False, "reasoning": "API key not configured."}

    prompt = (
        VERIFICATION_PROMPT_TEMPLATE.format(
            full_text=finding.full_text,
            pattern_type=finding.pattern_type,
            matched_string=finding.matched_string
        )
    )
    
    try:
        response = model.generate_content(prompt)
        decision = response.text.strip().upper()
        is_real = (decision == "REAL")
        
        # A simple reasoning for now. This could be more elaborate.
        reasoning = f"Gemini classified the finding as '{decision}'."
        
        return {
            "is_real_risk": is_real,
            "risk_level": "HIGH" if is_real else "NONE",
            "reasoning": reasoning
        }
    except Exception as e:
        print(f"Error calling Gemini API for verification: {e}")
        return {"is_real_risk": False, "reasoning": str(e)}


def draft_coaching(user: str, finding: Finding, verdict: dict) -> dict:
    """
    Uses Gemini to draft a coaching message for the user.
    Returns a dictionary with the drafted message.
    """
    if not model:
        print("Cannot draft coaching, Gemini model not configured.")
        return {}

    prompt = COACHING_PROMPT_TEMPLATE.format(
        user=user,
        full_text=finding.full_text,
        pattern_type=finding.pattern_type
    )
    
    try:
        response = model.generate_content(prompt)
        message_body = response.text.strip()
        return {
            "recipient_user": user,
            "message_body": message_body
        }
    except Exception as e:
        print(f"Error calling Gemini API for coaching: {e}")
        return {}

# --- 3. Test Block ---
if __name__ == "__main__":
    # Test with a finding that should be a false positive
    test_finding = Finding(
        pattern_type="AWS_ACCESS_KEY",
        matched_string="AKIAIOSFODNN7EXAMPLE",
        full_text="I can't get the S3 bucket to list files. I'm using this key: AKIAIOSFODNN7EXAMPLE",
        message_id="msg_002"
    )
    
    print("🕵️ Running Sentinel (Verification)...")
    verdict_result = verify_finding(test_finding)
    print(f"Verdict: {verdict_result}")
    
    print("\n" + "-"*20 + "\n")

    # Test with a finding that should be a real risk
    real_finding = Finding(
        pattern_type="CREDIT_CARD",
        matched_string="4532 1234 5678 9012",
        full_text="Can someone process a refund for this client? Card is 4532 1234 5678 9012, exp 12/26.",
        message_id="msg_004"
    )
    
    print("🕵️ Running Sentinel (Verification)...")
    real_verdict = verify_finding(real_finding)
    print(f"Verdict: {real_verdict}")

    if real_verdict.get("is_real_risk"):
        print("\n🤖 Running Coach (Drafting)...")
        coaching_draft = draft_coaching(user="david_sales", finding=real_finding, verdict=real_verdict)
        print(f"Draft: {coaching_draft}")
