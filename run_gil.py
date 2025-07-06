"""
GAIA Initiative Loop (GIL) Runner

This script acts as the autonomous "heartbeat" for GAIA. It runs on a schedule,
checks for system idleness, and if idle, processes a high-priority topic.
"""

import logging
import time
import os
import schedule
from typing import Dict, Any
# MODIFICATION: Import datetime and timedelta for time calculations
from datetime import datetime, timedelta

# Core GAIA components
from app.cognition.agent_core import AgentCore
from app.cognition.topic_manager import prioritize_topics
from gaia_rescue import MinimalAIManager

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",
)
logger = logging.getLogger("GAIA.InitiativeLoop")

# --- Constants ---
GIL_SESSION_ID = "gaia_initiative_loop_session"
TOPIC_CACHE_PATH = "app/shared/topic_cache.json"
# MODIFICATION: Add constants for the idleness check
LAST_ACTIVITY_FILE = "app/shared/last_activity.timestamp"
IDLE_THRESHOLD_MINUTES = 15


def execute_initiative_turn():
    """
    Performs a single autonomous "thought" cycle for GAIA, but only if the
    system has been idle for a sufficient amount of time.
    """
    # MODIFICATION: Check for idleness before doing anything else
    try:
        if os.path.exists(LAST_ACTIVITY_FILE):
            with open(LAST_ACTIVITY_FILE, 'r', encoding='utf-8') as f:
                last_activity_str = f.read().strip()

            last_activity_time = datetime.fromisoformat(last_activity_str)
            idle_duration = datetime.utcnow() - last_activity_time

            if idle_duration < timedelta(minutes=IDLE_THRESHOLD_MINUTES):
                logger.info(
                    f"System is not idle (last activity {idle_duration.total_seconds():.0f}s ago). "
                    f"Skipping GIL turn."
                )
                return  # Exit the function early
    except (IOError, ValueError) as e:
        logger.warning(f"Could not read or parse last activity timestamp: {e}. Assuming idle.")

    logger.info("🧠 System is idle. Waking up to check for high-priority topics...")

    # 1. Prioritize topics to find the most important thing to think about.
    top_topics = prioritize_topics(TOPIC_CACHE_PATH, top_n=1)
    if not top_topics:
        logger.info("🧘 No active topics to process. GAIA is at peace. Sleeping.")
        return

    current_topic: Dict[str, Any] = top_topics[0]
    topic_id = current_topic.get("topic_id")
    topic_desc = current_topic.get("topic")

    logger.info(f"🎯 Selected highest priority topic: [{topic_id}] - {topic_desc}")

    # 2. Formulate a prompt *to itself* to work on the topic.
    self_prompt = f"""
    [Autonomous Reflection Cycle]
    My current highest-priority, unresolved topic is: '{topic_desc}'.
    The topic's metadata is: {current_topic}.

    My task is to analyze this topic and decide on the next step.
    - If I have enough information to resolve it, I will use the `resolve_topic` primitive.
    - If I need to do more work or break it down, I will use the `update_topic` primitive to update its status or the `add_topic` primitive to create sub-tasks.
    - If the task requires writing code or a document, I will use the `ai.write` primitive.

    Based on this, what is my next logical action?
    """

    # 3. Initialize the agent and use the existing AgentCore to run the turn.
    try:
        ai_manager = MinimalAIManager()
        ai_manager.initialize()
        agent_core = AgentCore(ai_manager)

        logger.info("🚀 Handing self-generated prompt to AgentCore...")
        for event in agent_core.run_turn(user_input=self_prompt, session_id=GIL_SESSION_ID):
            if event['type'] != 'token':
                logger.debug(f"GIL Event: {event}")

        logger.info("✅ GIL turn complete.")

    except Exception as e:
        logger.error(f"❌ An error occurred during the GIL turn: {e}", exc_info=True)


if __name__ == "__main__":
    # MODIFICATION: The schedule is now just a check interval, not a fixed run time.
    CHECK_INTERVAL_SECONDS = 60
    logger.info(
        f"--- GAIA Initiative Loop (GIL) started. "
        f"Will check for {IDLE_THRESHOLD_MINUTES} min of idleness every {CHECK_INTERVAL_SECONDS} seconds. ---"
    )

    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(execute_initiative_turn)

    # Initial run immediately for testing
    execute_initiative_turn()

    while True:
        schedule.run_pending()
        time.sleep(1)