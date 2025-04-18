# GAIA Web Interface Implementation Guide

Follow this guide to implement the web interface for your GAIA D&D Campaign Assistant.

## Directory Structure

Your project should have the following structure:

```
campaign-project/
├── campaign-data/
│   ├── core-documentation/
│   ├── generated_documentation/
│   └── raw-data/
├── models/
│   └── Hermes-3-Llama-3.2-3B.Q4_K_M.gguf
├── chroma_db/
├── logs/
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── main.py
├── web_app.py
├── gaia_instructions.txt
├── Dockerfile
└── docker-compose.yml
```

## Implementation Steps

1. **Create the required directories**:
   ```bash
   mkdir -p templates static/css static/js logs
   ```

2. **Create the HTML file**:
   ```bash
   nano templates/index.html
   ```
   Copy the contents from the templates/index.html artifact.

3. **Create the CSS file**:
   ```bash
   nano static/css/styles.css
   ```
   Copy the contents from both parts of the static/css/styles.css artifacts.

4. **Create the JavaScript file**:
   ```bash
   nano static/js/app.js
   ```
   Copy the contents from both parts of the static/js/app.js artifacts.

5. **Create the web application file**:
   ```bash
   nano web_app.py
   ```
   Copy the contents from the web_app.py artifact.

6. **Update the Dockerfile**:
   ```bash
   nano Dockerfile
   ```
   Replace with the contents from the Updated Dockerfile with Web Interface Support artifact.

7. **Update docker-compose.yml**:
   ```bash
   nano docker-compose.yml
   ```
   Replace with the contents from the Updated docker-compose.yml with Web Interface Support artifact.

## Building and Running the Web Interface

1. **Build the updated Docker image**:
   ```bash
   docker-compose build
   ```

2. **Run the container**:
   ```bash
   docker-compose up
   ```

3. **Access the web interface**:
   Open your browser and navigate to:
   ```
   http://localhost:7860
   ```

## Feature Overview

The web interface provides:

1. **Chat Interface**: Interact with GAIA through a modern chat interface
2. **Document Management**: Browse, view, and search through campaign documents
3. **File Upload**: Upload raw campaign notes for automatic processing
4. **Artifact Generation**: Create artifacts through the chat interface
5. **Mobile Responsiveness**: Works on desktop and mobile devices

## Troubleshooting

1. **If the web interface doesn't load**:
   - Check Docker logs with `docker-compose logs`
   - Ensure port 7860 is not in use by another application
   - Verify that all files are in the correct locations

2. **If initialization fails**:
   - Check that your model file path is correct in docker-compose.yml
   - Ensure you have enough memory allocated to Docker
   - Check the logs in the logs/ directory

3. **If uploads don't work**:
   - Ensure the campaign-data/raw-data directory is writable
   - Check file permissions
   - Verify the file type is supported (.txt, .rtf, .docx, .md)

## Customization

1. **Change the theme**:
   - Edit the CSS variables at the top of static/css/styles.css
   - The primary colors can be changed to match your campaign's theme

2. **Add more features**:
   - The JavaScript in app.js is modular and can be extended
   - Flask routes in web_app.py can be expanded for additional functionality

3. **Increase GPU usage**:
   - If you have a capable GPU, increase the N_GPU_LAYERS value in docker-compose.yml
