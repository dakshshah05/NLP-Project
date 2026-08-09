"""
AURA AI -- Command Testing Script
==================================
Usage:
    python test_commands.py                    # Run all built-in test cases
    python test_commands.py "your command"     # Test a single custom command
    python test_commands.py --live             # Interactive REPL mode

Setup (set your Groq key first):
    Windows : set GROQ_API_KEY=gsk_xxxxxxxxxx
    Linux   : export GROQ_API_KEY=gsk_xxxxxxxxxx
"""

import os, sys, json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

os.environ.setdefault(
    "FIREBASE_CREDENTIALS_JSON",
    '{"type":"service_account","project_id":"mock","private_key_id":"x","private_key":"-----BEGIN RSA PRIVATE KEY-----\nMIIEpA==\n-----END RSA PRIVATE KEY-----\n","client_email":"mock@mock.iam.gserviceaccount.com","client_id":"0","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token"}'
)

from backend.app.nlp.processor import NLPProcessor
processor = NLPProcessor()

G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; R = "\033[91m"; X = "\033[0m"; B = "\033[1m"

TEST_CASES = [
    {"label": "English: PDF + Email",         "cmd": "Create a PDF on How to use Gemini and send it to daksh.kumar@bcah.christuniversity.in",                "expect_intent": "SEND_EMAIL",       "expect_recipient": "daksh.kumar@bcah.christuniversity.in"},
    {"label": "Hindi: PDF बनाएं + भेजें",      "cmd": "Gemini का इस्तेमाल कैसे करें, इस पर एक PDF बनाएँ और उसे daksh.kumar@bcah.christuniversity.in पर भेजें", "expect_intent": "SEND_EMAIL",       "expect_recipient": "daksh.kumar@bcah.christuniversity.in"},
    {"label": "Hinglish: PDF banao + bhejo",  "cmd": "Artificial Intelligence pe ek PDF banao aur use john@example.com ko bhejo",                           "expect_intent": "SEND_EMAIL",       "expect_recipient": "john@example.com"},
    {"label": "English: PDF only",            "cmd": "Generate a PDF report on Climate Change and its effects on global warming",                             "expect_intent": "CREATE_DOCUMENT",  "expect_recipient": None},
    {"label": "English: Plain email",         "cmd": "Send an email to priya@office.com with subject Project Update saying deadline is next Friday",          "expect_intent": "SEND_EMAIL",       "expect_recipient": "priya@office.com"},
    {"label": "Hindi: Plain email",           "cmd": "rohan@gmail.com par ek email bhejo, vishay: Meeting kal subah 10 baje",                                "expect_intent": "SEND_EMAIL",       "expect_recipient": "rohan@gmail.com"},
    {"label": "Kannada: PDF + email",         "cmd": "test@example.com ge ek PDF email madi, vishay: Bharat itihas",                                         "expect_intent": "SEND_EMAIL",       "expect_recipient": "test@example.com"},
    {"label": "English: Schedule meeting",    "cmd": "Schedule a team meeting tomorrow at 10 AM with the marketing department",                               "expect_intent": "PLAN_SCHEDULE",    "expect_recipient": None},
    {"label": "English: Find document",       "cmd": "Find the sales report PDF from last month in my workspace",                                             "expect_intent": "FIND_DOCUMENT",    "expect_recipient": None},
    {"label": "English: Manage files",        "cmd": "Compress the workspace folder and create a backup archive",                                             "expect_intent": "MANAGE_FILES",     "expect_recipient": None},
]

def show(r):
    e = r.get("entities", {})
    print(f"  {B}Intent{X}    : {C}{r['intent']}{X} ({r['intent_confidence']*100:.0f}%)")
    print(f"  {B}Language{X}  : {r['language']}")
    print(f"  {B}Topic{X}     : {e.get('file_topic') or '—'}")
    print(f"  {B}Recipient{X} : {e.get('recipient') or '—'}")
    print(f"  {B}Filename{X}  : {e.get('filename') or '—'}")
    print(f"  {B}Create PDF{X}: {e.get('create_file', False)}")
    print(f"  {B}Nodes{X}     : {[n['id'] for n in r.get('task_decomposition',[])]}")

def run_single(cmd, label="Custom", expect_intent=None, expect_recipient=None):
    print(f"\n{B}{'─'*58}{X}")
    print(f"{B}[{label}]{X}")
    print(f"  Cmd: {Y}{cmd}{X}")
    r = processor.process_command(cmd)
    show(r)
    ok = True
    if expect_intent and r["intent"] != expect_intent:
        print(f"  {R}✗ Expected intent={expect_intent}, got {r['intent']}{X}")
        ok = False
    if expect_recipient:
        got = str((r.get("entities") or {}).get("recipient", "")).lower()
        if expect_recipient.lower() not in got:
            print(f"  {R}✗ Expected recipient '{expect_recipient}', got '{got}'{X}")
            ok = False
    if ok: print(f"  {G}✓ PASSED{X}")
    return ok

def run_all():
    print(f"\n{B}{'='*58}")
    print("  AURA AI NLP Test Suite")
    print(f"{'='*58}{X}")
    eng = "Groq (Llama-3.3-70B)" if os.getenv("GROQ_API_KEY") else "Local NLTK fallback (set GROQ_API_KEY for full power)"
    print(f"  Engine: {C}{eng}{X}\n")
    passed = sum(run_single(**c) for c in TEST_CASES)
    col = G if passed == len(TEST_CASES) else Y
    print(f"\n{B}{'='*58}")
    print(f"  {col}{passed}/{len(TEST_CASES)} tests passed{X}")
    print(f"{'='*58}{X}\n")

def live():
    print(f"\n{B}AURA AI Interactive Tester{X} — type 'quit' to exit\n")
    while True:
        try:
            cmd = input(f"{C}> {X}").strip()
            if not cmd or cmd.lower() in ("quit","exit","q"): break
            run_single(cmd)
        except KeyboardInterrupt: break
    print("Bye!")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--live" in args: live()
    elif args: run_single(" ".join(args))
    else: run_all()

