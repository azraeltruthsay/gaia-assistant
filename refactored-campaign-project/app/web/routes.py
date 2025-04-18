"""
Web routes for GAIA D&D Campaign Assistant.
Defines all Flask routes for the web interface.
"""

import os
import logging
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app
from werkzeug.utils import secure_filename

from app.utils.helpers import sanitize_filename, clean_response, get_file_extension

# Get the logger
logger = logging.getLogger("GAIA")

# Create the blueprint
web_bp = Blueprint('web', __name__)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'txt', 'rtf', 'docx', 'md'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@web_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@web_bp.route('/api/status')
def status():
    """Return the initialization status of the AI."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    return jsonify({
        'initialized': ai_manager is not None,
        'error': current_app.config.get('INIT_ERROR')
    })

@web_bp.route('/api/query', methods=['POST'])
def query():
    """Process a query to the AI."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    data = request.json
    query_text = data.get('query', '')
    
    if not query_text:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Check if this is an artifact generation request
        if query_text.lower().startswith('artifact:'):
            artifact_prompt = query_text[len('artifact:'):].strip()
            artifact_path = ai_manager.generate_artifact(artifact_prompt)
            
            if not artifact_path:
                return jsonify({'error': 'Failed to generate artifact'}), 500
            
            # Get filename from path
            artifact_filename = os.path.basename(artifact_path)
            
            # Add to history
            ai_manager.add_to_history(f"User: {query_text}")
            ai_manager.add_to_history(f"Generated artifact: {artifact_filename}")
            
            response = f"I've prepared the artifact you requested. It's been stored as '{artifact_filename}'."
            
            return jsonify({
                'response': response,
                'artifact': artifact_filename
            })
        else:
            # Process normal query
            response = ai_manager.query_campaign_world(query_text)
            
            # Clean response
            response = clean_response(response)
            
            # Add to history
            ai_manager.add_to_history(f"User: {query_text}")
            ai_manager.add_to_history(f"GAIA: {response}")
            
            return jsonify({'response': response})
                
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/history')
def get_history():
    """Get the conversation history."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    return jsonify({'history': ai_manager.conversation_history})

@web_bp.route('/api/documents')
def list_documents():
    """List all available documents."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    try:
        # List core documentation
        core_docs = []
        for filename in os.listdir(ai_manager.config.data_path):
            if filename.endswith('.md'):
                filepath = os.path.join(ai_manager.config.data_path, filename)
                doc_info = ai_manager.doc_processor.get_document_info(filepath)
                if doc_info:
                    core_docs.append(doc_info)
        
        # List generated artifacts
        artifacts = []
        for filename in os.listdir(ai_manager.config.output_path):
            if filename.endswith('.md'):
                filepath = os.path.join(ai_manager.config.output_path, filename)
                doc_info = ai_manager.doc_processor.get_document_info(filepath)
                if doc_info:
                    artifacts.append(doc_info)
        
        return jsonify({
            'core_documentation': core_docs,
            'artifacts': artifacts
        })
    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/document/<path:filename>')
def get_document(filename):
    """Get the content of a specific document."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    try:
        # Check in core documentation
        core_path = os.path.join(ai_manager.config.data_path, filename)
        if os.path.exists(core_path):
            with open(core_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'type': 'core'})
        
        # Check in artifacts
        artifact_path = os.path.join(ai_manager.config.output_path, filename)
        if os.path.exists(artifact_path):
            with open(artifact_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'type': 'artifact'})
        
        # Check in external code path - Add this section
        code_path = os.path.join(ai_manager.config.external_code_path, filename)
        if os.path.exists(code_path):
            try:
                with open(code_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return jsonify({'content': content, 'type': 'code'})
            except UnicodeDecodeError:
                # Try with a different encoding for binary files
                with open(code_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return jsonify({'content': content, 'type': 'code'})
        
        return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving document: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file to the raw data directory."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(ai_manager.config.raw_data_path, filename)
        file.save(file_path)
        
        # Process the uploaded file
        try:
            processed = False
            raw_text = ai_manager.doc_processor.extract_text_from_file(file_path)
            if raw_text:
                markdown_content = ai_manager.doc_processor.convert_to_markdown(raw_text)
                if markdown_content:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_filename = f"converted_{os.path.splitext(filename)[0]}_{timestamp}.md"
                    output_filepath = os.path.join(ai_manager.config.output_path, output_filename)
                    if ai_manager.doc_processor.save_markdown(output_filepath, markdown_content):
                        processed = True
                        
                        # Update vector store with new content
                        new_documents = ai_manager.doc_processor.load_and_preprocess_data(ai_manager.config.output_path)
                        if new_documents:
                            ai_manager.vector_store_manager.update_vector_store(ai_manager.vector_store, new_documents)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'processed': processed
            })
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}", exc_info=True)
            return jsonify({'error': str(e), 'filename': filename}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@web_bp.route('/downloads/<path:filename>')
def download_file(filename):
    """Download a document file."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return "AI not initialized yet", 503
    
    # Check if file exists in core documentation
    if os.path.exists(os.path.join(ai_manager.config.data_path, filename)):
        return send_from_directory(ai_manager.config.data_path, filename, as_attachment=True)
    
    # Check if file exists in artifacts
    if os.path.exists(os.path.join(ai_manager.config.output_path, filename)):
        return send_from_directory(ai_manager.config.output_path, filename, as_attachment=True)
    
    return "File not found", 404

@web_bp.route('/api/conversation/summary', methods=['GET'])
def get_conversation_summary():
    """Get a summary of the current conversation."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    try:
        # Force summarization and archiving
        summary = ai_manager.summarize_and_archive_conversation()
        return jsonify({
            'success': True,
            'summary': summary or "No summary available"
        })
    except Exception as e:
        logger.error(f"Error generating conversation summary: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/conversation/archives', methods=['GET'])
def get_conversation_archives():
    """Get a list of archived conversations."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    try:
        # Get summaries from conversation manager
        summaries = ai_manager.conversation_manager.summaries
        
        # Format for response
        archives = []
        for summary in summaries:
            archives.append({
                'id': summary['id'],
                'timestamp': summary['timestamp'],
                'summary': summary['summary'],
                'keywords': summary.get('keyword_phrases', [])
            })
        
        return jsonify({
            'success': True,
            'archives': archives
        })
    except Exception as e:
        logger.error(f"Error retrieving conversation archives: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/conversation/archive/<archive_id>', methods=['GET'])
def get_conversation_archive(archive_id):
    """Get a specific archived conversation."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    try:
        # Get archived conversation
        content = ai_manager.conversation_manager.get_archived_conversation(archive_id)
        
        if not content:
            return jsonify({'error': 'Archive not found'}), 404
        
        return jsonify({
            'success': True,
            'id': archive_id,
            'content': content
        })
    except Exception as e:
        logger.error(f"Error retrieving archive {archive_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
        
@web_bp.route('/api/conversation/relevant', methods=['POST'])
def get_relevant_conversations():
    """Get archived conversations relevant to a query."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        # Find relevant conversations
        relevant = ai_manager.conversation_manager.find_relevant_context(query)
        
        return jsonify({
            'success': True,
            'relevant_conversations': relevant
        })
    except Exception as e:
        logger.error(f"Error finding relevant conversations: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
        
@web_bp.route('/api/code', methods=['GET'])
def list_code_files():
    """List all code files available for analysis."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    try:
        code_files = []
        
        # List files in code paths
        for root, dirs, files in os.walk(ai_manager.config.external_code_path):
            for file in files:
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, ai_manager.config.external_code_path)
                
                # Only include text files
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        # Just try to read the first few bytes to confirm it's text
                        f.read(1024)
                        
                    # Get language
                    language = ai_manager.code_analyzer.identify_language(filepath)
                    
                    # Only include recognized code files
                    if language != 'unknown':
                        code_files.append({
                            'path': relative_path,
                            'language': language,
                            'full_path': filepath
                        })
                except:
                    # Not a text file or couldn't be read, skip
                    pass
        
        return jsonify({
            'success': True,
            'code_files': code_files
        })
    except Exception as e:
        logger.error(f"Error listing code files: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/code/analyze', methods=['POST'])
def analyze_code():
    """Analyze a specific code file."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    data = request.json
    filepath = data.get('filepath', '')
    
    if not filepath:
        return jsonify({'error': 'File path cannot be empty'}), 400
    
    # Validate path is within external code path
    full_path = os.path.join(ai_manager.config.external_code_path, filepath)
    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Analyze the code
        content = ai_manager.code_analyzer.load_code_file(full_path)
        if not content:
            return jsonify({'error': 'Failed to load code file'}), 500
            
        analysis = ai_manager.code_analyzer.analyze_code_with_llm(full_path, content)
        
        if not analysis:
            return jsonify({'error': 'Failed to analyze code'}), 500
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error analyzing code: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
        
@web_bp.route('/api/code/file', methods=['GET'])
def get_code_file():
    """Get the content of a specific code file."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    filepath = request.args.get('filepath', '')
    
    if not filepath:
        return jsonify({'error': 'File path cannot be empty'}), 400
    
    try:
        # Build the full path from the external code path
        full_path = os.path.join(ai_manager.config.external_code_path, filepath)
        
        # Check if file exists
        if not os.path.exists(full_path):
            return jsonify({'error': f'File not found at {filepath}'}), 404
        
        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with a different encoding for binary files
            with open(full_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Get file language
        language = ai_manager.code_analyzer.identify_language(full_path)
        
        return jsonify({
            'success': True,
            'content': content,
            'language': language,
            'path': filepath,
            'full_path': full_path
        })
    except Exception as e:
        logger.error(f"Error retrieving code file: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
        
@web_bp.route('/api/code/upload', methods=['POST'])
def upload_code_file():
    """Upload a file to the external code directory."""
    ai_manager = current_app.config.get('AI_MANAGER')
    
    if not ai_manager:
        return jsonify({'error': 'AI not initialized yet'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Create target directory structure
    directory = request.form.get('directory', '')
    target_dir = os.path.join(ai_manager.config.external_code_path, directory)
    
    # Ensure the directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(target_dir, filename)
    file.save(file_path)
    
    # Process the uploaded file
    try:
        # Check if it's a text file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                return jsonify({'error': 'File is not a text file'}), 400
        
        # Create chunks for the file
        language = ai_manager.code_analyzer.identify_language(file_path)
        file_chunks = ai_manager.code_analyzer.create_code_chunks(file_path, content)
        
        # Update vector store with new chunks
        if file_chunks and ai_manager.vector_store:
            ai_manager.vector_store_manager.update_vector_store(ai_manager.vector_store, file_chunks)
            
        return jsonify({
            'success': True,
            'filename': filename,
            'language': language,
            'chunks': len(file_chunks)
        })
    except Exception as e:
        logger.error(f"Error processing uploaded code file: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500