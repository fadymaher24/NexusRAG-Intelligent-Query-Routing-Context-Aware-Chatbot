"""
Strategy pattern for query routing and handling.
Different strategies for FAQ and Product queries.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json

from app.models import QueryType, TaskNature, Product, ProductMetadata
from app.repositories import FAQRepository, ProductRepository
from app.llm_client import LLMClient
from app.config import config
from app.utils.logger import logger


class QueryClassifier:
    """Classifier for determining query type and nature."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize classifier.
        
        Args:
            llm_client: LLM client for classification
        """
        self.llm_client = llm_client
    
    def classify_query_type(self, query: str) -> QueryType:
        """Classify query as FAQ or Product.
        
        Args:
            query: User query
            
        Returns:
            QueryType enum value
        """
        prompt = f"""
Label the following instruction as an FAQ-related query or a product-related query.

Product-related queries are specific to product information or require using product details to answer.
Products are clothes from a store.
An FAQ question addresses common inquiries such as policies, refunds, shipping, or general help.

Examples:
Is there a refund for incorrectly bought clothes? Label: FAQ
Tell me about the cheapest T-shirts that you have. Label: Product
Do you have blue T-shirts under 100 dollars? Label: Product
I bought a T-shirt and I didn't like it. How can I get a refund? Label: FAQ
How long does delivery usually take? Label: FAQ

Return only one of the two labels: FAQ or Product.

Instruction: {query}
Label:
"""
        
        try:
            label = self.llm_client.generate_single_token(prompt, temperature=0.0)
            logger.info(f"Query classified as: {label}")
            
            if label == "FAQ":
                return QueryType.FAQ
            elif label == "Product":
                return QueryType.PRODUCT
            else:
                logger.warning(f"Unexpected classification label: {label}")
                return QueryType.UNKNOWN
        except Exception as e:
            logger.error(f"Failed to classify query type: {e}", exc_info=True)
            return QueryType.UNKNOWN
    
    def classify_task_nature(self, query: str) -> TaskNature:
        """Classify query as creative or technical.
        
        Args:
            query: User query
            
        Returns:
            TaskNature enum value
        """
        prompt = f"""
Decide if the following query requires creativity (creating, composing, making new things)
or technical information (product details, prices, availability, etc.).
Label it as creative or technical.

Examples:
Give me suggestions on a nice look for a nightclub. Label: creative
What are the blue dresses you have available? Label: technical
Give me three T-shirts for summer. Label: technical
Give me a look for attending a wedding party. Label: creative

Query to be analyzed: {query}
Only output one token: the label.
"""
        
        try:
            label = self.llm_client.generate_single_token(prompt, temperature=0.0)
            logger.info(f"Task nature classified as: {label}")
            
            if label == "creative":
                return TaskNature.CREATIVE
            elif label == "technical":
                return TaskNature.TECHNICAL
            else:
                logger.warning(f"Unexpected task nature label: {label}")
                return TaskNature.UNKNOWN
        except Exception as e:
            logger.error(f"Failed to classify task nature: {e}", exc_info=True)
            return TaskNature.UNKNOWN


class QueryStrategy(ABC):
    """Abstract base class for query handling strategies."""
    
    @abstractmethod
    def handle(self, query: str) -> Dict[str, Any]:
        """Handle the query and return response parameters.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with prompt and LLM parameters
        """
        pass


class FAQQueryStrategy(QueryStrategy):
    """Strategy for handling FAQ queries."""
    
    def __init__(
        self,
        faq_repository: FAQRepository,
        llm_client: LLMClient
    ):
        """Initialize FAQ query strategy.
        
        Args:
            faq_repository: Repository for FAQ data
            llm_client: LLM client for generating responses
        """
        self.faq_repo = faq_repository
        self.llm_client = llm_client
        logger.info("Initialized FAQQueryStrategy")
    
    def handle(self, query: str) -> Dict[str, Any]:
        """Handle FAQ query.
        
        Args:
            query: User FAQ query
            
        Returns:
            Dictionary with prompt and parameters for LLM
        """
        logger.info(f"Handling FAQ query: {query}")
        
        # Get FAQ layout
        faq_layout = self.faq_repo.get_faq_layout()
        
        # Create prompt
        prompt = f"""
You will be provided with an FAQ for a clothing store.
Answer the instruction based ONLY on the provided FAQ.
You may use more than one FAQ entry if needed.
Only answer the question asked and do not mention the FAQ explicitly.

<FAQ>
PROVIDED FAQ:
{faq_layout}
</FAQ>

Question: {query}
"""
        
        return {
            'prompt': prompt,
            'temperature': config.TEMPERATURE_DEFAULT,
            'top_p': config.TOP_P_DEFAULT,
            'max_tokens': config.MAX_TOKENS_DEFAULT
        }


class ProductQueryStrategy(QueryStrategy):
    """Strategy for handling Product queries."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        llm_client: LLMClient,
        classifier: QueryClassifier
    ):
        """Initialize Product query strategy.
        
        Args:
            product_repository: Repository for product data
            llm_client: LLM client for generating responses
            classifier: Query classifier for task nature
        """
        self.product_repo = product_repository
        self.llm_client = llm_client
        self.classifier = classifier
        logger.info("Initialized ProductQueryStrategy")
    
    def extract_metadata(self, query: str) -> Optional[ProductMetadata]:
        """Extract product metadata from query.
        
        Args:
            query: User query
            
        Returns:
            ProductMetadata object or None
        """
        # Get all possible values for each field
        products = self.product_repo.get_all()
        
        if not products:
            logger.warning("No products available for metadata extraction")
            return None
        
        values = {
            'gender': set(),
            'masterCategory': set(),
            'articleType': set(),
            'baseColour': set(),
            'season': set(),
            'usage': set()
        }
        
        for product in products:
            values['gender'].add(product.gender)
            values['masterCategory'].add(product.master_category)
            values['articleType'].add(product.article_type)
            values['baseColour'].add(product.base_colour)
            values['season'].add(product.season)
            values['usage'].add(product.usage)
        
        # Convert sets to lists for JSON serialization
        values = {k: list(v) for k, v in values.items()}
        
        prompt = f"""
A query will be provided. Based on this query, a vector database will be searched to find relevant clothing items.
Generate a JSON object containing useful metadata to filter products for this query.
The possible values for each feature are given in the following JSON: {json.dumps(values)}

Provide a JSON containing the features that best match the query (values should be in lists, multiple values possible).
If a price range is mentioned, include a price key specifying the range (between values, greater than, or less than).
Return only the JSON, nothing else. The price key must be a JSON object with "min" and "max" values (use 0 if no lower bound, and "inf" if no upper bound).
Always include the following keys: gender, masterCategory, articleType, baseColour, price, usage, and season.
If no price is specified, set min = 0 and max = inf.
Include only values present in the JSON above.

Example of expected JSON:

{{
  "gender": ["Women"],
  "masterCategory": ["Apparel"],
  "articleType": ["Dresses"],
  "baseColour": ["Blue"],
  "price": {{"min": 0, "max": "inf"}},
  "usage": ["Formal"],
  "season": ["All seasons"]
}}

Query: {query}
"""
        
        try:
            metadata_dict = self.llm_client.generate_json(prompt)
            if metadata_dict:
                metadata = ProductMetadata.from_dict(metadata_dict)
                logger.info(f"Extracted metadata: {metadata}")
                return metadata
            else:
                logger.warning("Failed to extract metadata from query")
                return None
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}", exc_info=True)
            return None
    
    def handle(self, query: str) -> Dict[str, Any]:
        """Handle Product query.
        
        Args:
            query: User product query
            
        Returns:
            Dictionary with prompt and parameters for LLM
        """
        logger.info(f"Handling Product query: {query}")
        
        # Classify task nature
        task_nature = self.classifier.classify_task_nature(query)
        
        # Get LLM parameters based on task nature
        llm_params = config.get_llm_params(task_nature.value)
        
        # Extract metadata and retrieve relevant products
        metadata = self.extract_metadata(query)
        
        relevant_products = self.product_repo.search_with_adaptive_filtering(
            query=query,
            metadata=metadata,
            limit=config.PRODUCT_LIMIT,
            min_results=config.MIN_RESULTS_THRESHOLD
        )
        
        # Generate context from products
        context = "\n".join([p.to_context_string() for p in relevant_products])
        
        # Create prompt
        prompt = (
            f"Given the available set of cloth products, answer the question that follows, "
            f"providing the item ID in your answers. "
            f"Other information might be provided but not necessarily all of them; "
            f"pick only the relevant ones for the given query and avoid being too long when describing the items' features. "
            f"If no number of products is mentioned in the query, select at most five to show. "
            f"CLOTH PRODUCTS AVAILABLE: {context} "
            f"QUERY: {query}"
        )
        
        return {
            'prompt': prompt,
            'temperature': llm_params['temperature'],
            'top_p': llm_params['top_p'],
            'max_tokens': config.MAX_TOKENS_DEFAULT,
            'task_nature': task_nature,
            'products': relevant_products
        }


class QueryRouter:
    """Router for directing queries to appropriate strategies."""
    
    def __init__(
        self,
        faq_strategy: FAQQueryStrategy,
        product_strategy: ProductQueryStrategy,
        classifier: QueryClassifier
    ):
        """Initialize query router.
        
        Args:
            faq_strategy: Strategy for FAQ queries
            product_strategy: Strategy for Product queries
            classifier: Query classifier
        """
        self.faq_strategy = faq_strategy
        self.product_strategy = product_strategy
        self.classifier = classifier
        logger.info("Initialized QueryRouter")
    
    def route(self, query: str) -> Dict[str, Any]:
        """Route query to appropriate strategy.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with response parameters
        """
        logger.info(f"Routing query: {query}")
        
        # Classify query type
        query_type = self.classifier.classify_query_type(query)
        
        # Route to appropriate strategy
        if query_type == QueryType.FAQ:
            result = self.faq_strategy.handle(query)
            result['query_type'] = query_type
            return result
        elif query_type == QueryType.PRODUCT:
            result = self.product_strategy.handle(query)
            result['query_type'] = query_type
            return result
        else:
            logger.warning(f"Unknown query type, using default response")
            return {
                'prompt': f"User provided a question that does not fit FAQ or Product related questions. "
                          f"Answer it based on the context you already have so far. Query provided by the user: {query}",
                'query_type': query_type,
                'temperature': config.TEMPERATURE_DEFAULT,
                'top_p': config.TOP_P_DEFAULT,
                'max_tokens': config.MAX_TOKENS_DEFAULT
            }
