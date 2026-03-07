"""
Flask API for NexusRAG chatbot.
Provides RESTful endpoints for chatbot interactions.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from typing import Dict, Any
import os

from app.services import ServiceFactory
from app.config import config
from app.utils.logger import logger
from app.utils.tracing import TraceContext, trace_operation


def create_app() -> Flask:
    """Create and configure Flask application.
    
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    CORS(app)
    
    # Disable Flask's default logger in production
    if not config.FLASK_DEBUG:
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    # Initialize service with lazy loading pattern
    service = None
    service_initialized = False
    
    def get_service():
        """Get or initialize service instance (lazy loading for Flask 3.x)."""
        nonlocal service, service_initialized
        if not service_initialized:
            try:
                logger.info("Initializing chatbot service...")
                service = ServiceFactory.get_service()
                service.setup()
                service_initialized = True
                logger.info("Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize service: {e}", exc_info=True)
                service_initialized = True  # Prevent retry loops
        return service
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint.
        
        Returns:
            JSON with status
        """
        return jsonify({
            'status': 'healthy',
            'service': 'NexusRAG Chatbot'
        }), 200
    
    @app.route('/api/query', methods=['POST'])
    def handle_query():
        """Handle chatbot query.
        
        Expected JSON:
        {
            "query": "user query string"
        }
        
        Returns:
            JSON with response
        """
        # Generate trace ID for this request
        trace_id = TraceContext.generate_trace_id()
        TraceContext.set_trace_id(trace_id)
        
        try:
            with trace_operation("handle_query_request"):
                # Get query from request
                data = request.get_json()
                
                if not data or 'query' not in data:
                    return jsonify({
                        'error': 'Missing query parameter',
                        'trace_id': trace_id
                    }), 400
                
                query = data['query']
                
                if not query or not query.strip():
                    return jsonify({
                        'error': 'Empty query',
                        'trace_id': trace_id
                    }), 400
                
                logger.info(f"[trace_id={trace_id}] Received query: {query}")
                
                # Get service instance
                service = get_service()
                if service is None:
                    return jsonify({
                        'success': False,
                        'error': 'Service not initialized',
                        'trace_id': trace_id
                    }), 500
                
                # Process query
                response = service.process_query(query)
                
                # Add trace ID to response
                response_dict = response.to_dict()
                response_dict['trace_id'] = trace_id
                
                # Return response
                return jsonify(response_dict), 200
            
        except Exception as e:
            logger.error(f"[trace_id={trace_id}] Error handling query: {e}", exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'details': str(e),
                'trace_id': trace_id
            }), 500
        finally:
            TraceContext.clear_trace_id()
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Simple chat endpoint that returns just the response text.
        
        Expected JSON:
        {
            "message": "user message"
        }
        
        Returns:
            JSON with response text
        """
        try:
            data = request.get_json()
            
            if not data or 'message' not in data:
                return jsonify({
                    'error': 'Missing message parameter'
                }), 400
            
            message = data['message']
            
            if not message or not message.strip():
                return jsonify({
                    'error': 'Empty message'
                }), 400
            
            logger.info(f"Received chat message: {message}")
            
            # Get service instance
            service = get_service()
            if service is None:
                return jsonify({
                    'success': False,
                    'error': 'Service not initialized'
                }), 500
            
            # Process query
            response = service.process_query(message)
            
            if response.success:
                return jsonify({
                    'response': response.response,
                    'query_type': response.query_type.value
                }), 200
            else:
                return jsonify({
                    'error': response.error or 'Failed to process message'
                }), 500
            
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return jsonify({
                'error': 'Internal server error'
            }), 500
    
    @app.route('/', methods=['GET'])
    def index():
        """Serve simple web interface."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexusRAG Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 800px;
            width: 100%;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .chat-content {
            padding: 30px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .response-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        
        .response-section.show {
            display: block;
        }
        
        .response-section h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .response-text {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        
        .metadata {
            margin-top: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .metadata span {
            display: inline-block;
            margin-right: 15px;
            padding: 5px 10px;
            background: white;
            border-radius: 5px;
        }
        
        .error {
            color: #dc3545;
            padding: 15px;
            background: #fff5f5;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛍️ NexusRAG Chatbot</h1>
            <p>Fashion Forward Hub - Your AI Shopping Assistant</p>
        </div>
        
        <div class="chat-content">
            <div class="input-group">
                <label for="query">Ask me anything about our products or policies:</label>
                <textarea 
                    id="query" 
                    placeholder="e.g., Do you have blue T-shirts? or What is your return policy?"
                ></textarea>
            </div>
            
            <button id="submitBtn" onclick="submitQuery()">Send Message</button>
            
            <div id="response" class="response-section">
                <h3>Response:</h3>
                <div id="responseContent"></div>
            </div>
        </div>
    </div>
    
    <script>
        async function submitQuery() {
            const query = document.getElementById('query').value.trim();
            const responseDiv = document.getElementById('response');
            const responseContent = document.getElementById('responseContent');
            const submitBtn = document.getElementById('submitBtn');
            
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            // Show loading
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            responseDiv.classList.add('show');
            responseContent.innerHTML = '<div class="loading"><div class="spinner"></div><p>Thinking...</p></div>';
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    let html = `<div class="response-text">${data.response}</div>`;
                    
                    if (data.query_type || data.task_nature) {
                        html += '<div class="metadata">';
                        if (data.query_type) {
                            html += `<span><strong>Type:</strong> ${data.query_type}</span>`;
                        }
                        if (data.task_nature) {
                            html += `<span><strong>Nature:</strong> ${data.task_nature}</span>`;
                        }
                        html += '</div>';
                    }
                    
                    responseContent.innerHTML = html;
                } else {
                    responseContent.innerHTML = `<div class="error">Error: ${data.error || 'Unknown error'}</div>`;
                }
            } catch (error) {
                responseContent.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Message';
            }
        }
        
        // Allow Enter key to submit (Shift+Enter for new line)
        document.getElementById('query').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        });
    </script>
</body>
</html>
        """
        return render_template_string(html)
    
    @app.teardown_appcontext
    def cleanup(error=None):
        """Cleanup on application teardown."""
        nonlocal service
        if service:
            service.cleanup()
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting Flask server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
