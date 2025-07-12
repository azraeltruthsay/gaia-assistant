# GAIA - General Artisanal Intelligence Architecture

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/azraeltruthsay/gaia-assistant)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/azraeltruthsay/gaia-assistant/blob/main/LICENSE)
[![Project Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/azraeltruthsay/gaia-assistant)

GAIA (General Artisanal Intelligence Architecture) is a versatile and adaptable AI partner for a variety of tasks, including project management, content generation, and code analysis.

## About The Project

GAIA is a sophisticated AI assistant designed to be a modular and extensible platform for AI-powered assistance. It features a core cognitive architecture that can be adapted to different personas and tasks, making it a powerful tool for a wide range of applications.

### Key Features

*   **Modular and Extensible**: The system is designed to be easily extended with new features, personas, and capabilities.
*   **Multi-Model Support**: The `ModelPool` allows for the use of multiple AI models, enabling the system to select the best model for each task.
*   **Context-Aware and Persona-Driven**: The `PromptBuilder` ensures that the AI's responses are always grounded in the current context and consistent with its active persona.
*   **Self-Reflection and Refinement**: The `SelfReflection` module enables the AI to learn from its mistakes and improve its performance over time.
*   **Real-Time Monitoring and Safety**: The `StreamObserver` and ethics modules provide a robust safety net to prevent the AI from generating harmful or inappropriate content.
*   **Multiple Interfaces**: The system can be accessed through a CLI, a web interface, and a developer-focused rescue shell.

### Technology Stack

*   **Backend**: Python with Flask
*   **AI**: `llama-cpp-python` for local LLM inference
*   **Vector Database**: ChromaDB for retrieval-augmented generation
*   **Frontend**: HTML, CSS, JavaScript
*   **Containerization**: Docker and Docker Compose

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

4.  **Build and run the container:**

    ```bash
    docker-compose up --build
    ```

## Usage

### Web Interface

The web interface provides a user-friendly way to interact with GAIA. It can be accessed at `http://localhost:7860`.

### Command-Line Interface (CLI)

The CLI provides a more direct way to interact with GAIA. It can be accessed by running the following command:

```bash
docker-compose run --rm gaia-assistant python main.py
```

### Rescue Shell

The rescue shell is a developer-focused environment for interacting with GAIA's core components. It can be accessed by running the following command:

```bash
docker-compose run --rm gaia-assistant python gaia_rescue.py
```

## Architecture Overview

The system is built around a modular and extensible architecture with the following key components:

*   **`AgentCore`**: The central cognitive engine that orchestrates the entire "Reason-Act-Reflect" loop.
*   **`ModelPool`**: Manages a pool of AI models, allowing the system to use different models for different tasks.
*   **`PromptBuilder`**: Constructs detailed, context-aware prompts for the LLM.
*   **`SelfReflection`**: Enables the AI to analyze and refine its own plans and responses.
*   **`StreamObserver`**: Monitors the LLM's output in real-time to detect and prevent errors.
*   **`OutputRouter`**: Parses the structured output from the LLM and routes it to the appropriate destination.
*   **`SessionManager`**: Manages conversation history and long-term memory.
*   **`EthicalSentinel` and `CoreIdentityGuardian`**: Ensure that the AI's behavior remains within ethical boundaries.

## Roadmap

*   [ ] Expanded context windows
*   [ ] Project switching functionality
*   [ ] User authentication system
*   [ ] Dynamic context management with archiving
*   [ ] Image generation capabilities
*   [ ] Conversation summarization with filtering
*   [ ] Smart context archiving and retrieval
*   [ ] LoRA fine-tuning during system idle time
*   [ ] Content importance weighting for memory management
*   [ ] Incremental vector database updates
*   [ ] Enhanced templating system
*   [ ] Improved artifact editing
*   [ ] Real-time knowledge updates
*   [ ] Multi-project support
*   [ ] Optimizations for larger models
*   [ ] Backup and versioning systems

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for more information.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
