import os
import google.generativeai as genai
from dotenv import load_dotenv
from scanner import Finding
from adk import Agent

# Initial API Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ No API Key found in .env file! Please add GOOGLE_API_KEY.")

genai.configure(api_key=api_key)

# Defining Tools
# Global vars to capture the agent's output for our main loop
latest_verdict = {}
latest_draft = {}

def submit_verdict(is_real_risk: bool, risk_level: str, reasoning: str):
    """
    Call this tool to submit your security analysis decision.
    
    Args:
        is_real_risk: True if this is a REAL secret/PII. False if it is test data.
        risk_level: 'LOW', 'MEDIUM', or 'HIGH'.
        reasoning: Brief explanation of why you made this decision.
    """
    global latest_verdict
    latest_verdict = {
        "is_real_risk": is_real_risk,
        "risk_level": risk_level,
        "reasoning": reasoning
    }
    return "Verdict recorded."

def send_notification(recipient_user: str, message_body: str):
    """
    Call this tool to draft the alert message.
    """
    global latest_draft
    latest_draft = {
        "recipient_user": recipient_user,
        "message_body": message_body
    }
    return "Draft recorded."

#Initializing our agents
MODEL_NAME = "gemini-2.0-flash"
print(f"🤖 Initializing Agents with model: {MODEL_NAME}")

sentinel_agent = Agent(
    model=MODEL_NAME,
    system_instruction=(
        "You are a Senior Security Analyst. Analyze the text context. "
        "Distinguish between REAL credentials (Risk) and TEST/DOCS (Safe). "
        "You MUST call the 'submit_verdict' tool to finish."
    ),
    tools=[submit_verdict]
)

coach_agent = Agent(
    model=MODEL_NAME,
    system_instruction=(
        "You are PrivacyPal, a friendly security assistant. "
        "Your job is to send a private Slack DM to a user. "
        "Start with 'Hi [User] 👋'. "
        "Politely explain that you found a security risk in their message. "
        "Tell them exactly what to do (e.g., 'Please delete the message and rotate the key'). "
        "Sign off with 'Thanks, PrivacyPal 🛡️'. "
        "You MUST call the 'send_notification' tool."
    ),
    tools=[send_notification]
)

# Defining Helper Functions to run our Agents
def verify_finding(finding: Finding):
    """Runs the Sentinel Agent"""
    global latest_verdict
    latest_verdict = {} # Reset
    
    prompt = (
        f"Analyze this finding:\n"
        f"Pattern: {finding.pattern_type}\n"
        f"Matched String: {finding.matched_string}\n"
        f"Context: \"{finding.full_text}\""
    )
    sentinel_agent.handle_message(prompt)
    
    return latest_verdict

def draft_coaching(user: str, verdict: dict):
    """Runs the Coach Agent"""
    global latest_draft
    latest_draft = {} # Reset
    
    prompt = (
        f"Draft a message for user '{user}'.\n"
        f"Risk: {verdict.get('risk_level')}\n"
        f"Reason: {verdict.get('reasoning')}"
    )
    
    coach_agent.handle_message(prompt)
    
    return latest_draft