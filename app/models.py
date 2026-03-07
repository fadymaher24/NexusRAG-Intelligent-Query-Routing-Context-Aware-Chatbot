"""
Data models for NexusRAG application.
Defines the structure for products, FAQs, and query responses.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class QueryType(Enum):
    """Enumeration for query types."""
    FAQ = "FAQ"
    PRODUCT = "Product"
    UNKNOWN = "Unknown"


class TaskNature(Enum):
    """Enumeration for task nature."""
    CREATIVE = "creative"
    TECHNICAL = "technical"
    UNKNOWN = "unknown"


@dataclass
class Product:
    """Product data model."""
    product_id: str
    product_display_name: str
    gender: str
    master_category: str
    sub_category: str
    article_type: str
    base_colour: str
    season: str
    year: int
    usage: str
    price: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create Product instance from dictionary."""
        return cls(
            product_id=data.get('product_id', ''),
            product_display_name=data.get('productDisplayName', ''),
            gender=data.get('gender', ''),
            master_category=data.get('masterCategory', ''),
            sub_category=data.get('subCategory', ''),
            article_type=data.get('articleType', ''),
            base_colour=data.get('baseColour', ''),
            season=data.get('season', ''),
            year=int(data.get('year', 0)),
            usage=data.get('usage', ''),
            price=float(data.get('price', 0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Product to dictionary."""
        return {
            'product_id': self.product_id,
            'productDisplayName': self.product_display_name,
            'gender': self.gender,
            'masterCategory': self.master_category,
            'subCategory': self.sub_category,
            'articleType': self.article_type,
            'baseColour': self.base_colour,
            'season': self.season,
            'year': self.year,
            'usage': self.usage,
            'price': self.price
        }
    
    def to_context_string(self) -> str:
        """Convert Product to context string for LLM."""
        return (
            f"Product ID: {self.product_id}. "
            f"Product name: {self.product_display_name}. "
            f"Product Category: {self.master_category}. "
            f"Product usage: {self.usage}. "
            f"Product gender: {self.gender}. "
            f"Product Type: {self.article_type}. "
            f"Product Sub-Category: {self.sub_category}. "
            f"Product Color: {self.base_colour}. "
            f"Product Season: {self.season}. "
            f"Product Price: ${self.price}. "
            f"Product Year: {self.year}."
        )


@dataclass
class FAQ:
    """FAQ data model."""
    question: str
    answer: str
    faq_type: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FAQ':
        """Create FAQ instance from dictionary."""
        return cls(
            question=data.get('question', ''),
            answer=data.get('answer', ''),
            faq_type=data.get('type', '')
        )
    
    def to_string(self) -> str:
        """Convert FAQ to string format."""
        return f"Question: {self.question} Answer: {self.answer} Type: {self.faq_type}"


@dataclass
class ProductMetadata:
    """Product metadata for filtering."""
    gender: Optional[List[str]] = field(default_factory=list)
    master_category: Optional[List[str]] = field(default_factory=list)
    article_type: Optional[List[str]] = field(default_factory=list)
    base_colour: Optional[List[str]] = field(default_factory=list)
    season: Optional[List[str]] = field(default_factory=list)
    usage: Optional[List[str]] = field(default_factory=list)
    price_min: Optional[float] = 0
    price_max: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductMetadata':
        """Create ProductMetadata from dictionary."""
        price = data.get('price', {})
        price_min = price.get('min', 0) if isinstance(price, dict) else 0
        price_max_raw = price.get('max') if isinstance(price, dict) else None
        price_max = None if price_max_raw == 'inf' else price_max_raw
        
        return cls(
            gender=data.get('gender', []),
            master_category=data.get('masterCategory', []),
            article_type=data.get('articleType', []),
            base_colour=data.get('baseColour', []),
            season=data.get('season', []),
            usage=data.get('usage', []),
            price_min=price_min,
            price_max=price_max
        )


@dataclass
class QueryResponse:
    """Response model for queries."""
    success: bool
    query_type: QueryType
    task_nature: Optional[TaskNature] = None
    response: str = ""
    products: Optional[List[Product]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'success': self.success,
            'query_type': self.query_type.value,
            'task_nature': self.task_nature.value if self.task_nature else None,
            'response': self.response,
            'products': [p.to_dict() for p in self.products] if self.products else None,
            'metadata': self.metadata,
            'error': self.error
        }
