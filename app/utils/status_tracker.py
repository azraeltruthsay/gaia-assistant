# /app/utils/status_tracker.py

class GAIAStatus:
    def __init__(self):
        self.step = "Starting initialization..."
        self.percent = 0
        self.complete = False

    def update(self, step: str, percent: int):
        self.step = step
        self.percent = percent
        self.complete = percent >= 100

    def get_status(self):
        return {
            "step": self.step,
            "percent": self.percent,
            "initialized": self.complete
        }

# Singleton instance used globally
GAIA_STATUS = GAIAStatus()
