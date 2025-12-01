import json
import time
import os
from colorama import Fore, Style, init

# Import our custom modules
from scanner import scan_message
from agents import verify_finding, draft_coaching

init(autoreset=True)

# Configuration
MOCK_DATA_PATH = "mock_data.json"
SLEEP_DELAY = 12  # Seconds between messages

def load_feed():
    """Reads the JSON file acting as our 'Slack Feed'."""
    if not os.path.exists(MOCK_DATA_PATH):
        print(f"{Fore.RED}❌ Error: Mock data file not found at {MOCK_DATA_PATH}")
        return []
    
    with open(MOCK_DATA_PATH, "r") as f:
        return json.load(f)

def run_privacy_pal():
    print(f"{Fore.CYAN}{Style.BRIGHT}🛡️  STARTING PRIVACYPAL SECURITY AGENT...")
    print(f"{Fore.CYAN}---------------------------------------------")
    
    # 1. Load the "World" state
    messages = load_feed()
    print(f"{Fore.BLUE}ℹ️  Loaded {len(messages)} messages from Slack feed.\n")
    
    # 2. Start the Loop
    for msg in messages:
        user = msg.get("user")
        text = msg.get("text")
        print(f"{Fore.WHITE}📥 Reading message from {Style.BRIGHT}{user}{Style.NORMAL}...")
        
        # --- PHASE 1: THE TRAP (Regex) ---
        findings = scan_message(msg)
        
        if not findings:
            # Safe message
            print(f"{Fore.GREEN}   ✅ Clean.")
        else:
            # Found a potential pattern!
            for finding in findings:
                print(f"{Fore.YELLOW}   ⚠️  TRAP TRIGGERED! Pattern: {finding.pattern_type}")
                print(f"{Fore.YELLOW}      Match: {finding.matched_string}")
                
                # --- PHASE 2: THE SENTINEL (Verification Agent) ---
                print(f"{Fore.MAGENTA}      🕵️  Sentinel Agent analyzing context...")
                verdict = verify_finding(finding)
                
                # Check the decision
                is_real_risk = verdict.get("is_real_risk", False)
                reasoning = verdict.get("reasoning", "No reason provided.")
                
                if not is_real_risk:
                    print(f"{Fore.GREEN}      ✅ FALSE POSITIVE. Sentinel says: {reasoning}")
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}      🚨 REAL RISK CONFIRMED! Severity: {verdict.get('risk_level')}")
                    print(f"{Fore.RED}         Reason: {reasoning}")
                    
                    # --- PHASE 3: THE COACH (Remediation Agent) ---
                    print(f"{Fore.MAGENTA}      ✍️  Coach Agent drafting alert...")
                    draft = draft_coaching(user, verdict)
                    
                    print(f"\n{Fore.CYAN}      [PRIVATE DM SENT TO {user.upper()}]")
                    print(f"{Fore.CYAN}      --------------------------------")
                    print(f"{Fore.WHITE}{Style.DIM}      {draft.get('message_body')}")
                    print(f"{Fore.CYAN}      --------------------------------\n")
        
        # Simulate processing time
        time.sleep(SLEEP_DELAY)

    print(f"{Fore.CYAN}---------------------------------------------")
    print(f"{Fore.CYAN}✅ SCAN COMPLETE.")

if __name__ == "__main__":
    run_privacy_pal()