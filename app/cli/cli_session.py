
from council_manager import CouncilManager
from model_stubs import Hermes, CodeMind, GAIALite
from resource_monitor import ResourceMonitor

# Initialize models (stubs for now)
models = {
    "Hermes": Hermes(),
    "CodeMind": CodeMind(),
    "GAIA-Lite": GAIALite()
}

# Initialize resource monitor (stub implementation)
resource_monitor = ResourceMonitor()

# Initialize CouncilManager
council = CouncilManager(models, resource_monitor)

def cli_loop():
    print("""
Welcome to the GAIA Council CLI.
Commands:
 - 'reflect': Process queued reflection topics.
 - 'state': Check GAIA's current mode.
 - Any other input will be queued as a reflection or interjection.
Type 'exit' to leave.
""")
    while True:
        user_input = input("> ")
        if user_input.strip().lower() == "exit":
            print("👋 Exiting Council CLI.")
            break
        elif user_input.strip().lower() == "reflect":
            council.process_reflections()
        elif user_input.strip().lower() == "state":
            print(f"GAIA is currently in {council.state} mode.")
        else:
            council.log_conversation(f"User: {user_input}")
            if council.session_active:
                print("🔔 Interjection received. Council pausing to consider input...")
                council.deliberate(user_input)
            else:
                council.queue_reflection(user_input)

if __name__ == "__main__":
    cli_loop()
