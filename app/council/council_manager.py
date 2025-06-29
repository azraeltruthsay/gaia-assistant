from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import requests

app = Flask(__name__)

# Path to the Council Chat Log
COUNCIL_CHAT_LOG = "./logs/council_chat.md"

# Ensure the log directory exists
os.makedirs(os.path.dirname(COUNCIL_CHAT_LOG), exist_ok=True)

VALID_MESSAGE_TYPES = {"proposal", "vote", "reflection", "decision", "broadcast", "escalation"}
VALID_SENDER_IDS = {"Lite", "Prime", "CodeMind"}
OPTIONAL_PAYLOAD_KEYS = {"task", "urgency", "vote", "reason", "recommended_target", "result", "context_summary", "token_count", "original_task_type", "task_id"}

# Send a GCP message to the local GCP server
def send_gcp_message(sender_id, message_type, payload):
    payload = {k: v for k, v in payload.items() if v is not None}
    message = {
        "sender_id": sender_id,
        "message_type": message_type,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        r = requests.post("http://localhost:5050/gcp", json=message)
        if r.status_code == 200:
            print(f"✅ Sent {message_type.upper()} message from {sender_id}")
        else:
            print(f"❌ GCP message failed: {r.text}")
    except Exception as e:
        print(f"❌ Exception in send_gcp_message: {e}")

# GCP server endpoint to receive messages
@app.route("/gcp", methods=["POST"])
def handle_gcp_message():
    message = request.get_json()
    if not message:
        return jsonify({"error": "No JSON payload"}), 400

    required_fields = ["sender_id", "message_type", "payload", "timestamp"]
    missing = [field for field in required_fields if field not in message]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    sender = message["sender_id"]
    if sender not in VALID_SENDER_IDS:
        return jsonify({"error": f"Invalid sender_id: {sender}"}), 400

    msg_type = message["message_type"]
    if msg_type not in VALID_MESSAGE_TYPES:
        return jsonify({"error": f"Invalid message_type: {msg_type}"}), 400

    payload = message["payload"]
    for key in payload:
        if key not in OPTIONAL_PAYLOAD_KEYS:
            return jsonify({"error": f"Unexpected payload key: {key}"}), 400

    # Log message to Council Chat
    try:
        with open(COUNCIL_CHAT_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{message['timestamp']}] {sender} ({msg_type.upper()}):\n")
            f.write(json.dumps(payload, indent=2))
            f.write("\n")
    except Exception as e:
        return jsonify({"error": f"Failed to log message: {e}"}), 500

    return jsonify({"status": "GCP message received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
