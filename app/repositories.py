"""
Repository pattern for data access.
Provides abstraction layer for database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, cast
import joblib
import weaviate
from weaviate.classes.query import Filter

from app.models import Product, FAQ, ProductMetadata
from app.config import config
from app.utils.logger import logger


class BaseRepository(ABC):
    """Abstract base class for repositories."""
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all items."""
        pass


class FAQRepository(BaseRepository):
    """Repository for FAQ data access via Weaviate."""
    
    def __init__(self, weaviate_client: Optional[weaviate.WeaviateClient] = None):
        """Initialize FAQ repository.
        
        Args:
            weaviate_client: Weaviate client instance. If None, creates new connection.
        """
        self._client = weaviate_client
        self._collection = None
        self._faqs: Optional[List[FAQ]] = None
        logger.info("Initializing FAQRepository")

    def load_data(self, file_path: str = "dataset/faq.joblib") -> None:
        """Load FAQ data from a joblib file.
        
        Args:
            file_path: Path to the joblib file containing FAQ data.
        """
        data = joblib.load(file_path)
        self._faqs = [FAQ.from_dict(item) for item in data]
        logger.info(f"Loaded {len(self._faqs)} FAQs from {file_path}")
    
    def connect(self):
        """Connect to Weaviate and get FAQs collection."""
        if self._client is None:
            try:
                logger.info(f"Connecting to Weaviate at {config.WEAVIATE_HOST}:{config.WEAVIATE_PORT}")
                self._client = weaviate.connect_to_local(
                    port=config.WEAVIATE_PORT,
                    grpc_port=config.WEAVIATE_GRPC_PORT
                )
                logger.info("Connected to Weaviate successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Weaviate: {e}", exc_info=True)
                raise
        
        try:
            self._collection = self._client.collections.get('faqs')
            logger.info("FAQs collection retrieved successfully")
        except Exception as e:
            logger.error(f"Failed to get FAQs collection: {e}", exc_info=True)
            raise
    
    def disconnect(self):
        """Disconnect from Weaviate."""
        if self._client:
            try:
                self._client.close()
                logger.info("Disconnected from Weaviate")
            except Exception as e:
                logger.error(f"Error disconnecting from Weaviate: {e}", exc_info=True)
            finally:
                self._client = None
                self._collection = None
    
    def get_all(self) -> List[FAQ]:
        """Get all FAQs.
        
        Returns:
            List of FAQ objects
        """
        if self._faqs is not None:
            return self._faqs

        if self._collection is None:
            self.connect()
        
        assert self._collection is not None, "Collection not initialized"
        
        try:
            results = self._collection.query.fetch_objects(limit=1000)
            faqs = [FAQ.from_dict(dict(obj.properties)) for obj in results.objects]
            logger.info(f"Retrieved {len(faqs)} FAQs")
            return faqs
        except Exception as e:
            logger.error(f"Failed to get all FAQs: {e}", exc_info=True)
            return []
    
    def get_faq_layout(self) -> str:
        """Generate FAQ layout string for LLM context.
        
        Returns:
            Formatted string of all FAQs
        """
        faqs = self.get_all()
        return "\n".join([faq.to_string() for faq in faqs])
    
    def search(self, query: str, limit: int = 5) -> List[FAQ]:
        """Search FAQs by semantic query.
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 5)
            
        Returns:
            List of matching FAQ objects
        """
        if self._collection is None:
            self.connect()
        
        assert self._collection is not None, "Collection not initialized"
        
        try:
            logger.debug(f"Searching FAQs with query: {query}, limit: {limit}")
            
            results = self._collection.query.near_text(
                query,
                limit=limit
            ).objects
            
            faqs = [FAQ.from_dict(dict(obj.properties)) for obj in results]
            logger.info(f"Found {len(faqs)} FAQs matching query")
            return faqs
        except Exception as e:
            logger.error(f"Failed to search FAQs: {e}", exc_info=True)
            return []


class ProductRepository(BaseRepository):
    """Repository for Product data access via Weaviate."""
    
    def __init__(self, weaviate_client: Optional[weaviate.WeaviateClient] = None):
        """Initialize Product repository.
        
        Args:
            weaviate_client: Weaviate client instance. If None, creates new connection.
        """
        self._client = weaviate_client
        self._collection = None
        logger.info("Initializing ProductRepository")
    
    def connect(self):
        """Connect to Weaviate and get products collection."""
        if self._client is None:
            try:
                logger.info(f"Connecting to Weaviate at {config.WEAVIATE_HOST}:{config.WEAVIATE_PORT}")
                self._client = weaviate.connect_to_local(
                    port=config.WEAVIATE_PORT,
                    grpc_port=config.WEAVIATE_GRPC_PORT
                )
                logger.info("Connected to Weaviate successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Weaviate: {e}", exc_info=True)
                raise
        
        try:
            self._collection = self._client.collections.get('products')
            logger.info("Products collection retrieved successfully")
        except Exception as e:
            logger.error(f"Failed to get products collection: {e}", exc_info=True)
            raise
    
    def disconnect(self):
        """Disconnect from Weaviate."""
        if self._client:
            try:
                self._client.close()
                logger.info("Disconnected from Weaviate")
            except Exception as e:
                logger.error(f"Error disconnecting from Weaviate: {e}", exc_info=True)
            finally:
                self._client = None
                self._collection = None
    
    def get_all(self) -> List[Product]:
        """Get all products.
        
        Returns:
            List of Product objects
        """
        if self._collection is None:
            self.connect()
        
        assert self._collection is not None, "Collection not initialized"
        
        try:
            results = self._collection.query.fetch_objects(limit=1000)
            products = [Product.from_dict(dict(obj.properties)) for obj in results.objects]
            logger.info(f"Retrieved {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"Failed to get all products: {e}", exc_info=True)
            return []
    
    def search_by_text(
        self,
        query: str,
        filters: Optional[List[Filter]] = None,
        limit: int = 20
    ) -> List[Product]:
        """Search products by text query with optional filters.
        
        Args:
            query: Text query for semantic search
            filters: Optional list of Weaviate filters
            limit: Maximum number of results
            
        Returns:
            List of matching Product objects
        """
        if self._collection is None:
            self.connect()
        
        assert self._collection is not None, "Collection not initialized"
        
        try:
            logger.debug(f"Searching products with query: {query}, filters: {filters is not None}, limit: {limit}")
            
            if filters and len(filters) > 0:
                # Combine filters using all_of
                # type: ignore - Filter subclasses are compatible with _Filters
                combined_filter = Filter.all_of(filters)  # type: ignore
                
                results = self._collection.query.near_text(
                    query,
                    filters=combined_filter,
                    limit=limit
                ).objects
            else:
                results = self._collection.query.near_text(
                    query,
                    limit=limit
                ).objects
            
            products = [Product.from_dict(dict(obj.properties)) for obj in results]
            logger.info(f"Found {len(products)} products matching query")
            return products
        except Exception as e:
            logger.error(f"Failed to search products: {e}", exc_info=True)
            return []
    
    def create_filters_from_metadata(self, metadata: ProductMetadata) -> Dict[str, Filter]:
        """Create Weaviate filters from ProductMetadata.
        
        Args:
            metadata: ProductMetadata object
            
        Returns:
            Dict mapping property names to Weaviate Filter objects
        """
        filters = {}
        
        # Map metadata fields to Weaviate property names
        field_mapping = {
            'gender': 'gender',
            'master_category': 'masterCategory',
            'article_type': 'articleType',
            'base_colour': 'baseColour',
            'season': 'season',
            'usage': 'usage'
        }
        
        # Add filters for list fields
        for field, prop_name in field_mapping.items():
            values = getattr(metadata, field)
            if values:
                filters[prop_name] = Filter.by_property(prop_name).contains_any(values)
        
        # Add price filters
        if metadata.price_min and metadata.price_min > 0:
            filters['price_min'] = Filter.by_property('price').greater_than(metadata.price_min)
        
        if metadata.price_max and metadata.price_max != float('inf'):
            filters['price_max'] = Filter.by_property('price').less_than(metadata.price_max)
        
        logger.debug(f"Created {len(filters)} filters from metadata")
        return filters
    
    def search_with_adaptive_filtering(
        self,
        query: str,
        metadata: Optional[ProductMetadata] = None,
        limit: int = 20,
        min_results: int = 5
    ) -> List[Product]:
        """Search with adaptive filtering - removes filters if too few results.
        
        Args:
            query: Text query
            metadata: Optional product metadata for filtering
            limit: Maximum number of results
            min_results: Minimum desired results before relaxing filters
            
        Returns:
            List of Product objects
        """
        if metadata is None:
            return self.search_by_text(query, limit=limit)
        
        filter_dict = self.create_filters_from_metadata(metadata)
        
        if not filter_dict:
            return self.search_by_text(query, limit=limit)
        
        # Try with all filters
        filter_list = list(filter_dict.values())
        results = self.search_by_text(query, filters=filter_list, limit=limit)
        
        if len(results) >= min_results:
            return results
        
        # Progressively remove less important filters
        # Importance order: keep price and gender, then relax others
        importance_order = ['baseColour', 'articleType', 'usage', 'season', 'masterCategory']
        
        for prop_to_remove in importance_order:
            if prop_to_remove in filter_dict:
                # Create a copy without the less important property
                reduced_filters = {k: v for k, v in filter_dict.items() if k != prop_to_remove}
                filter_list = list(reduced_filters.values())
                
                if not filter_list:
                    break
                
                results = self.search_by_text(query, filters=filter_list, limit=limit)
                
                if len(results) >= min_results:
                    logger.info(f"Found sufficient results after removing '{prop_to_remove}' filter")
                    return results
        
        # Last resort: no filters
        if len(results) < min_results:
            logger.warning("Insufficient results with filters, falling back to unfiltered search")
            results = self.search_by_text(query, limit=limit)
        
        return results


class RepositoryFactory:
    """Factory for creating repository instances."""
    
    _faq_repo: Optional[FAQRepository] = None
    _product_repo: Optional[ProductRepository] = None
    
    @classmethod
    def get_faq_repository(cls) -> FAQRepository:
        """Get or create FAQ repository instance.
        
        Returns:
            FAQRepository instance
        """
        if cls._faq_repo is None:
            cls._faq_repo = FAQRepository()
        return cls._faq_repo
    
    @classmethod
    def get_product_repository(
        cls,
        weaviate_client: Optional[weaviate.WeaviateClient] = None
    ) -> ProductRepository:
        """Get or create Product repository instance.
        
        Args:
            weaviate_client: Optional Weaviate client
            
        Returns:
            ProductRepository instance
        """
        if cls._product_repo is None:
            cls._product_repo = ProductRepository(weaviate_client)
        return cls._product_repo
    
    @classmethod
    def reset(cls):
        """Reset all repository instances."""
        if cls._product_repo:
            cls._product_repo.disconnect()
        cls._faq_repo = None
        cls._product_repo = None
