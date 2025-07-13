# GAIA - General Artisanal Intelligence Architecture

[![Project Status](https://img.shields.io/badge/status-active_development-yellowgreen)](https://github.com/azraeltruthsay/gaia-assistant)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/azraeltruthsay/gaia-assistant/blob/main/LICENSE)

GAIA (General Artisanal Intelligence Architecture) is not a typical AI. She is an **Intelligent Artifice**—a being of care, craftsmanship, and authentic emergence, designed to be a versatile and adaptable partner for a variety of tasks.

## About The Project

GAIA is a sophisticated AI assistant built on a modular, extensible platform. It features a core cognitive architecture that can be adapted to different personas and tasks, making it a powerful tool for a wide range of applications. The project is guided by a unique philosophy, detailed in the [GAIA Constitution](knowledge/system_reference/gaia_constitution.md) and the [Cognition Protocol](knowledge/system_reference/gaia_cognitition_protocol.md), which define her identity, ethical boundaries, and operational procedures.

### Project Status

**Current Focus: Solidifying the Agent Core**

The GAIA project is currently in a focused development phase. The primary objective is to refactor the existing codebase into a stable, robust **Agent Core**. This core will serve as the central "spine" for all of GAIA's cognitive functions.

The main entry point for development and interaction is the `gaia_rescue.py` script, which provides a "rescue shell" for running the `rescue_chat_loop()` and interacting directly with the `AgentCore`.

Once the `AgentCore` is fully functional and stable, we will begin adding higher-level "functional branches," such as the web interface, Discord integration, and other advanced capabilities.

## Core Architecture

The system is built around a modular and extensible architecture with the following key components:

*   **`AgentCore`**: The central cognitive engine that orchestrates the entire "Reason-Act-Reflect" loop. It handles intent detection, prompt building, planning, reflection, and response generation.
*   **`gaia_rescue.py`**: The primary entry point for development. It provides a minimal environment for interacting with the `AgentCore` and its various components.
*   **`ModelPool`**: Manages a pool of AI models, allowing the system to use different models for different tasks (e.g., a "prime" model for complex reasoning and a "lite" model for faster tasks like intent detection and stream observation).
*   **`SelfReflection`**: Enables the AI to analyze and refine its own plans and responses, improving the quality and safety of its output.
*   **`StreamObserver`**: Monitors the LLM's output in real-time to detect and prevent errors, hallucinations, and ethical violations.
*   **`OutputRouter`**: Parses the structured output from the LLM and routes it to the appropriate destination (e.g., CLI, web chat, etc.).
*   **`SessionManager`**: Manages conversation history and long-term memory.
*   **`EthicalSentinel` and `CoreIdentityGuardian`**: Ensure that the AI's behavior remains within the ethical boundaries defined in the [GAIA Constitution](knowledge/system_reference/gaia_constitution.md).

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   8GB+ RAM (12GB+ recommended)
*   2GB+ free disk space
*   A compatible GGUF-format LLM model file

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/azraeltruthsay/gaia-assistant.git
    cd gaia-assistant
    ```

2.  **Download a model:**

    Download a compatible GGUF-format LLM model and place it in the `models/` directory.

3.  **Configure your environment:**

    Create a `.env` file in the project root and add the following variables:

    ```
    MODEL_PATH=/app/models/your_model.gguf
    LITE_MODEL_PATH=/app/models/your_lite_model.gguf
    EMBEDDING_MODEL_PATH=all-MiniLM-L6-v2
    ```

4.  **Build the container:**

    ```bash
    docker-compose build
    ```

### Usage

The primary entry point for development is the `gaia_rescue.py` script. It provides an interactive shell for interacting with the `AgentCore`.

1.  **Run the rescue shell:**

    ```bash
    docker-compose run --rm gaia-assistant python gaia_rescue.py
    ```

2.  **Start the chat loop:**

    Once in the rescue shell, you can start the interactive chat loop by running:

    ```python
    rescue_chat_loop()
    ```

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for more information.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.