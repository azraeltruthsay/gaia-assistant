class OutputRouter:
    def __init__(self, default="chat-ui"):
        self.default = default

    def route(self, origin: str, task_type: str = "", purpose: str = "") -> str:
        if origin == "user":
            return "chat-ui"
        elif origin == "reflection":
            return "self-reflection"
        elif origin == "council":
            return "council"
        elif origin == "executor":
            return "shell-direct"
        return self.default
