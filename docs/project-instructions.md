# D&D Campaign AI Assistant (GAIA) - Project Instructions

## Project Overview

This project creates an AI-powered D&D campaign assistant named GAIA (pronounced "guy-uh") that can answer questions about your campaign world, generate campaign artifacts, and convert raw notes into structured documentation. GAIA is designed to function as an in-character AI integrated into a Warforged body in your D&D setting.

## Setup Instructions

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) and [Docker Compose](https://docs.docker.com/compose/install/)
- At least 8GB RAM recommended
- 2GB+ free disk space
- LLM model file (Hermes-3-Llama-3.2-3B.Q4_K_M.gguf or similar)

### Step 1: Prepare Directory Structure

Create the following directory structure:

```
campaign-project/
├── campaign-data/
│   ├── core-documentation/
│   ├── generated_documentation/
│   └── raw-data/
├── models/
├── chroma_db/
```

### Step 2: Download Required Files

1. Download the latest project files:
   - main.py
   - docker-compose.yml
   - Dockerfile
   - gaia_instructions.txt
   - campaign_tools.py

2. Download a compatible LLM model file such as Hermes-3-Llama-3.2-3B.Q4_K_M.gguf and place it in the `models/` directory.

### Step 3: Add Campaign Documentation

1. Place your Markdown campaign documents in `campaign-data/core-documentation/`
2. Place any raw text files (TXT, RTF, DOCX) you want to convert in `campaign-data/raw-data/`

### Step 4: Configure Environment

Check and modify your docker-compose.yml file if needed. The default configuration:

```yaml
version: '3.8'

services:
  campaign_llm:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./campaign-data:/app/campaign-data:rw
      - ./models/Hermes-3-Llama-3.2-3B.Q4_K_M.gguf:/app/model.gguf:ro
      - ./chroma_db:/app/chroma_db:rw
      - ./gaia_instructions.txt:/app/gaia_instructions.txt:ro
    environment:
      MODEL_PATH: /app/model.gguf
      DATA_PATH: /app/campaign-data/core-documentation
      RAW_DATA_PATH: /app/campaign-data/raw-data
      OUTPUT_PATH: /app/campaign-data/converted_raw
      VECTOR_DB_PATH: /app/chroma_db
      CORE_INSTRUCTIONS_FILE: /app/gaia_instructions.txt
    stdin_open: true
    tty: true
    restart: unless-stopped
```

### Step 5: Build and Run

From the project directory, run:

```bash
docker-compose up --build
```

The first run will:
1. Build the Docker image
2. Process your raw data files
3. Create embeddings for your campaign documents
4. Initialize the language model

## Using GAIA

### Interactive Mode

Once running, GAIA provides a command-line interface where you can:

1. Choose a text-to-speech voice (or press Enter for default)
2. Ask questions about your campaign world
3. Request artifact generation
4. Exit the application

#### Example Commands

```
Ask about your campaign world: What is BlueShot technology?
Ask about your campaign world: artifact: Create a table of important NPCs in Rogue's End
Ask about your campaign world: exit
```

### Campaign Tools

The `campaign_tools.py` script provides utilities for managing campaign content:

```bash
# Create template files
python campaign_tools.py create location "Rogue's End"
python campaign_tools.py create npc "Zarut"
python campaign_tools.py create item "BlueShot Crystal"

# List files
python campaign_tools.py list --dir core
python campaign_tools.py list --dir gen --pattern "*.md"

# Show document outline
python campaign_tools.py outline campaign-data/core-documentation/braeneage_general_info.md

# Backup all campaign data
python campaign_tools.py backup
```

## Customization Options

### Modify GAIA's Personality

Edit `gaia_instructions.txt` to change GAIA's character, behavior, and background knowledge. The file is structured into sections:

1. **CORE IDENTITY AND FUNCTION** - Basic character concept
2. **BACKGROUND KNOWLEDGE** - Information GAIA begins with
3. **INTERACTION GUIDELINES** - How GAIA should respond
4. **OPERATIONAL GUIDANCE** - Priority framework and formatting rules

### Change Model Settings

For better performance with different hardware:

1. Edit the `setup_llm` function in `main.py`:
   - Adjust `n_gpu_layers` to use GPU acceleration (if available)
   - Set `n_ctx` to change context window size
   - Modify `n_batch` for throughput optimization

2. Use a different model by:
   - Placing another GGUF model file in the `models/` directory
   - Updating the model path in `docker-compose.yml`

## Adding New Campaign Content

### Core Documentation

1. Create standard Markdown files for key aspects of your campaign
2. Use consistent header formats for better indexing
3. Place files in `campaign-data/core-documentation/`
4. Restart the application to update the knowledge base

### Template-Based Content

Use `campaign_tools.py` to create structured documents using built-in templates:

```bash
python campaign_tools.py create location "New Location"
```

### Converting Raw Notes

1. Place raw text files in `campaign-data/raw-data/`
2. The system will automatically convert them on startup
3. Converted files will appear in `campaign-data/converted_raw/`

## Troubleshooting

### Vector Database Issues

If ChromaDB fails to initialize:
1. Check permissions on the `chroma_db` directory
2. Try deleting the directory and restarting (will rebuild from your documents)

### Model Loading Problems

If the model fails to load:
1. Verify the path in docker-compose.yml is correct
2. Check that the model file exists and is not corrupted
3. For out-of-memory errors, try a smaller model or increase RAM allocation

### Text-to-Speech Issues

If TTS doesn't work:
1. Ensure your system has compatible TTS engines installed
2. Run the container with proper audio device access
3. Try a different voice option when prompted

## Advanced Features

### Creating Custom Templates

Modify `campaign_tools.py` to add your own template types:

1. Add a new template definition to the `templates` dictionary
2. Use the `{name}` placeholder for automatic substitution
3. Run with your new template type: `python campaign_tools.py create your_type "Name"`

### Extending GAIA's Capabilities

1. To add web API access, modify `main.py` to import and use appropriate libraries
2. For image generation, consider integrating with Stable Diffusion or similar services
3. To create a web interface, implement a Flask or FastAPI server in `main.py`

## Best Practices

1. **Structured Content**: Use consistent headers and formatting in your Markdown files
2. **Regular Backups**: Use `campaign_tools.py backup` before major changes
3. **Progressive Enhancement**: Start with core world information, then add details incrementally
4. **Query Testing**: Try different phrasings to find optimal question formats
5. **Performance Optimization**: Monitor memory usage and adjust model parameters accordingly
