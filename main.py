"""
Main entry point for NexusRAG Chatbot application.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services import ChatbotService, ServiceFactory
from app.api import create_app
from app.config import config
from app.utils.logger import logger


def run_cli():
    """Run chatbot in CLI mode."""
    logger.info("Starting NexusRAG Chatbot in CLI mode")
    
    print("=" * 60)
    print("NexusRAG Chatbot - Fashion Forward Hub")
    print("=" * 60)
    print("Type 'quit' or 'exit' to stop")
    print()
    
    # Initialize service
    with ServiceFactory.get_service() as service:
        while True:
            try:
                # Get user input
                query = input("You: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not query:
                    continue
                
                # Process query
                print("\nBot: ", end="", flush=True)
                response = service.process_query(query)
                
                if response.success:
                    print(response.response)
                    if response.query_type:
                        print(f"\n[Type: {response.query_type.value}]", end="")
                    if response.task_nature:
                        print(f" [Nature: {response.task_nature.value}]", end="")
                    print()
                else:
                    print(f"Error: {response.error}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in CLI: {e}", exc_info=True)
                print(f"\nError: {e}\n")


def run_server():
    """Run chatbot as Flask web server."""
    logger.info("Starting NexusRAG Chatbot in server mode")
    
    app = create_app()
    
    print("=" * 60)
    print("NexusRAG Chatbot - Server Mode")
    print("=" * 60)
    print(f"Server running at: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='NexusRAG - Intelligent Query Routing Context-Aware Chatbot'
    )
    
    parser.add_argument(
        '--mode',
        choices=['cli', 'server'],
        default='server',
        help='Run mode: cli for command-line interface, server for web API (default: server)'
    )
    
    parser.add_argument(
        '--host',
        default=config.FLASK_HOST,
        help=f'Server host (default: {config.FLASK_HOST})'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=config.FLASK_PORT,
        help=f'Server port (default: {config.FLASK_PORT})'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Update config with command-line arguments
    if args.host:
        config.FLASK_HOST = args.host
    if args.port:
        config.FLASK_PORT = args.port
    if args.debug:
        config.FLASK_DEBUG = True
        config.LOG_LEVEL = "DEBUG"
    
    # Run in selected mode
    if args.mode == 'cli':
        run_cli()
    else:
        run_server()


if __name__ == '__main__':
    main()
