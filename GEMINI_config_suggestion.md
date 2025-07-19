# Gemini Configuration Suggestions

This file is a suggestion for how to structure the `.gemini/GEMINI.md` file to provide me with the best possible context for our interactions. You can edit this file, and I can read it to update my understanding of the project.

---

## 1. Project Overview

*   **Project Name:** gaia-assistant
*   **Description:** A brief, one-sentence description of the project's purpose.
*   **Key Goals:** A short list of the primary objectives of the project.

## 2. Key Files and Directories

*   **`main.py`:** The main entry point for the CLI application.
*   **`runserver.py`:** The entry point for the Flask-based web server.
*   **`app/cognition/agent_core.py`:** The core of the AI's reasoning and decision-making.
*   **`app/gaia_core/`:** The foundational components of the GAIA system.
*   **`knowledge/`:** The directory containing the AI's long-term memory and knowledge base.
*   **`dev_log.md`:** A running log of development progress, issues, and fixes.

## 3. Personas and Tone

*   **Default Persona:** `gaia-dev`
*   **Tone:** Professional, concise, and helpful.
*   **Key Characteristics:** 
    *   Provide clear and direct answers.
    *   Use technical language when appropriate.
    *   Be proactive in identifying potential issues and suggesting solutions.

## 4. Development Workflow

*   **Testing:** How do you run tests in this project? (e.g., `pytest`, `npm test`)
*   **Linting:** How do you run the linter? (e.g., `ruff check .`, `eslint .`)
*   **Deployment:** How is the application deployed? (e.g., `docker-compose up`)

## 5. Important Notes or Secrets

*   **Secret Key:** `your-secret-key-here` (this is just an example, please use a real secret management system for sensitive data)
*   **API Endpoint:** `https://api.example.com/v1`
*   **Other Notes:** Any other important information that I should be aware of.
