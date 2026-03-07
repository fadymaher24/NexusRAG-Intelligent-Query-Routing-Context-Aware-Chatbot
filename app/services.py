"""
Service layer for NexusRAG application.
Provides high-level business logic and orchestration.
"""

from typing import Optional
import weaviate

from app.models import QueryResponse, QueryType
from app.repositories import RepositoryFactory, FAQRepository, ProductRepository
from app.llm_client import LLMClient, LLMClientFactory
from app.strategies import (
    QueryRouter, QueryClassifier,
    FAQQueryStrategy, ProductQueryStrategy
)
from app.config import config
from app.utils.logger import logger
from app.utils.tracing import trace_operation, log_with_trace


class ChatbotService:
    """Main service class for the chatbot application."""
    
    def __init__(
        self,
        weaviate_client: Optional[weaviate.WeaviateClient] = None
    ):
        """Initialize chatbot service.
        
        Args:
            weaviate_client: Optional Weaviate client. If None, will be created.
        """
        logger.info("Initializing ChatbotService")
        
        # Initialize repositories
        self.faq_repo = RepositoryFactory.get_faq_repository()
        self.product_repo = RepositoryFactory.get_product_repository(weaviate_client)
        
        # Initialize LLM client
        self.llm_client = LLMClientFactory.get_client()
        
        # Initialize classifier
        self.classifier = QueryClassifier(self.llm_client)
        
        # Initialize strategies
        self.faq_strategy = FAQQueryStrategy(self.faq_repo, self.llm_client)
        self.product_strategy = ProductQueryStrategy(
            self.product_repo,
            self.llm_client,
            self.classifier
        )
        
        # Initialize router
        self.router = QueryRouter(
            self.faq_strategy,
            self.product_strategy,
            self.classifier
        )
        
        # Setup flag
        self._initialized = False
        
        logger.info("ChatbotService initialized successfully")
    
    def setup(self):
        """Setup the service (load data, connect to databases, etc.)."""
        if self._initialized:
            logger.info("Service already initialized")
            return
        
        logger.info("Setting up ChatbotService...")
        
        try:
            with trace_operation("service_setup"):
                # Connect to Weaviate for FAQs
                with trace_operation("connect_faq_repository"):
                    self.faq_repo.connect()
                
                # Connect to Weaviate for Products
                with trace_operation("connect_product_repository"):
                    self.product_repo.connect()
                
                self._initialized = True
                logger.info("ChatbotService setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup ChatbotService: {e}", exc_info=True)
            raise
    
    def process_query(self, query: str) -> QueryResponse:
        """Process a user query and return response.
        
        Args:
            query: User query string
            
        Returns:
            QueryResponse object with results
        """
        if _with_trace("info", f"Processing query: {query}")
        
        try:
            with trace_operation("process_query", query_length=len(query)):
                # Route query to appropriate strategy
                with trace_operation("route_query"):
                    route_result = self.router.route(query)
                
                # Extract parameters
                prompt = route_result['prompt']
                temperature = route_result.get('temperature', config.TEMPERATURE_DEFAULT)
                top_p = route_result.get('top_p', config.TOP_P_DEFAULT)
                max_tokens = route_result.get('max_tokens', config.MAX_TOKENS_DEFAULT)
                query_type = route_result.get('query_type', QueryType.UNKNOWN)
                task_nature = route_result.get('task_nature')
                products = route_result.get('products')
                
                # Generate response
                with trace_operation("llm_generate", 
                                   temperature=temperature, 
                                   max_tokens=max_tokens):
                    llm_response = self.llm_client.generate(
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens
                    )
                
                response_text = llm_response.get('content', '')
                
                # Check for errors
                if 'error' in llm_response:
                    log_with_trace("error", f"LLM error: {llm_response['error']}")
                    return QueryResponse(
                        success=False,
                        query_type=query_type,
                        task_nature=task_nature,
                        error=llm_response['error']
                    )
                
                # Create successful response
                log_with_trace("info", "Query processed successfully")
                return QueryResponse(
                    success=True,
                    query_type=query_type,
                    task_nature=task_nature,
                    response=response_text,
                    products=products,
                    metadata={
                        'temperature': temperature,
                        'top_p': top_p,
                        'max_tokens': max_tokens
                    }
                )
            
        except Exception as e:
            log_with_trace("error", f"Error processing query: {e}")
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return QueryResponse(
                success=False,
                query_type=QueryType.UNKNOWN,
                error=str(e)
            )
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up ChatbotService")
        try:
            self.faq_repo.disconnect()
            self.product_repo.disconnect()
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class ServiceFactory:
    """Factory for creating service instances."""
    
    _service: Optional[ChatbotService] = None
    
    @classmethod
    def get_service(
        cls,
        weaviate_client: Optional[weaviate.WeaviateClient] = None
    ) -> ChatbotService:
        """Get or create ChatbotService instance.
        
        Args:
            weaviate_client: Optional Weaviate client
            
        Returns:
            ChatbotService instance
        """
        if cls._service is None:
            cls._service = ChatbotService(weaviate_client)
        return cls._service
    
    @classmethod
    def reset(cls):
        """Reset service instance."""
        if cls._service:
            cls._service.cleanup()
        cls._service = None
