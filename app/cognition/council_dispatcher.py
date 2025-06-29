import json
import time
import os
import logging
import requests
from datetime import datetime
from app.llm_wrappers import LiteLLM, PrimeLLM, CodeMindLLM
from app.utils.log_utils import write_to_thoughtstream, write_to_council_log

logger = logging.getLogger("GAIA.CouncilDispatcher")

# === Load Constants ===
constants_path = os.path.join(os.path.dirname(__file__), '..', 'gaia_constants.json')
with open(constants_path, 'r') as f:
    GAIA_CONSTANTS = json.load(f)

SAFE_EXECUTE_FUNCTIONS = set(GAIA_CONSTANTS["safe_execute_functions"])
COUNCIL_MODES = GAIA_CONSTANTS["council_modes"]

# === Initialize LLMs ===
COUNCIL_MEMBERS = {
    "Lite": LiteLLM(),
    "Prime": PrimeLLM(),
    "CodeMind": CodeMindLLM()
}

# === Dynamic Council State ===
council_state = {
    "Lite": {"status": "awake", "last_reflection": None},
    "Prime": {"status": "awake", "last_reflection": None},
    "CodeMind": {"status": "resting", "last_reflection": None}
}

def get_active_members():
    return [name for name, info in council_state.items() if info["status"] == "awake"]

def send_gcp_message(sender_id, message_type, payload):
    gcp_url = "http://localhost:5050/gcp"
    timestamp = datetime.utcnow().isoformat()
    message = {
        "sender_id": sender_id,
        "message_type": message_type,
        "payload": payload,
        "timestamp": timestamp
    }
    try:
        response = requests.post(gcp_url, json=message)
        if response.ok:
            print(f"✅ GCP message sent: {message_type}")
        else:
            print(f"❌ GCP message failed: {response.text}")
    except Exception as e:
        print(f"❌ Error sending GCP message: {e}")

def dispatch_thought(prompt, max_cycles=3, reflection_delay=2.0):
    logger.info("🧠 Starting council dispatch loop.")
    active_members = get_active_members()
    cycle_count = 0

    while active_members and cycle_count < max_cycles:
        for member_name in active_members:
            llm_instance = COUNCIL_MEMBERS[member_name]
            logger.info(f"🔍 {member_name} is reflecting... (Cycle {cycle_count + 1})")

            response = llm_instance.process_thought(
                task_type="council",
                persona=member_name,
                instructions="Reflect on the current state. Consider the last thought and context. Generate an actionable insight if needed.",
                payload=prompt,
                identity_intro=llm_instance.identity,
                reflect=True
            )

            timestamp = datetime.utcnow().isoformat()
            council_state[member_name]["last_reflection"] = timestamp

            # Log outputs
            write_to_thoughtstream(member_name, prompt, response)
            write_to_council_log(member_name, prompt, response)

            # 🚀 Send GCP message
            send_gcp_message(
                sender_id=member_name,
                message_type="reflection",
                payload={"response": response}
            )

            prompt = f"{member_name} reflected: {response}\nWhat are you thinking next?"

            time.sleep(reflection_delay)

        active_members = get_active_members()
        cycle_count += 1

    logger.info("✅ Council dispatch complete.")
    return "Council reflection cycle complete."

def update_council_state(member, status):
    """
    Update a council member's state (awake, resting, asleep).
    """
    if member in council_state:
        council_state[member]["status"] = status
        logger.info(f"🛌 Council member {member} is now {status}.")

def show_council_status():
    print("🌿 Current Council State:")
    for member, info in council_state.items():
        print(f"- {member}: {info['status']} (last reflection: {info['last_reflection']})")

