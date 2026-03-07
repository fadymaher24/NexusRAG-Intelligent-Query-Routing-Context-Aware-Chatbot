"""
Unit tests for NexusRAG application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Product, FAQ, ProductMetadata, QueryType, TaskNature
from app.config import config
from app.repositories import FAQRepository, ProductRepository


class TestModels(unittest.TestCase):
    """Test data models."""
    
    def test_product_from_dict(self):
        """Test Product creation from dictionary."""
        data = {
            'product_id': '123',
            'productDisplayName': 'Test Shirt',
            'gender': 'Men',
            'masterCategory': 'Apparel',
            'subCategory': 'Topwear',
            'articleType': 'Shirts',
            'baseColour': 'Blue',
            'season': 'Summer',
            'year': 2024,
            'usage': 'Casual',
            'price': 29.99
        }
        
        product = Product.from_dict(data)
        
        self.assertEqual(product.product_id, '123')
        self.assertEqual(product.product_display_name, 'Test Shirt')
        self.assertEqual(product.gender, 'Men')
        self.assertEqual(product.price, 29.99)
    
    def test_product_to_context_string(self):
        """Test Product context string generation."""
        product = Product(
            product_id='123',
            product_display_name='Test Shirt',
            gender='Men',
            master_category='Apparel',
            sub_category='Topwear',
            article_type='Shirts',
            base_colour='Blue',
            season='Summer',
            year=2024,
            usage='Casual',
            price=29.99
        )
        
        context = product.to_context_string()
        
        self.assertIn('Product ID: 123', context)
        self.assertIn('Test Shirt', context)
        self.assertIn('Blue', context)
    
    def test_faq_from_dict(self):
        """Test FAQ creation from dictionary."""
        data = {
            'question': 'What is the return policy?',
            'answer': 'Returns accepted within 30 days',
            'type': 'returns'
        }
        
        faq = FAQ.from_dict(data)
        
        self.assertEqual(faq.question, 'What is the return policy?')
        self.assertEqual(faq.answer, 'Returns accepted within 30 days')
        self.assertEqual(faq.faq_type, 'returns')


class TestConfig(unittest.TestCase):
    """Test configuration."""
    
    def test_config_singleton(self):
        """Test that Config is a singleton."""
        from app.config import Config
        
        config1 = Config()
        config2 = Config()
        
        self.assertIs(config1, config2)
    
    def test_get_llm_params(self):
        """Test LLM parameter retrieval."""
        creative_params = config.get_llm_params('creative')
        technical_params = config.get_llm_params('technical')
        
        self.assertIn('temperature', creative_params)
        self.assertIn('top_p', creative_params)
        self.assertGreater(creative_params['temperature'], technical_params['temperature'])


class TestRepositories(unittest.TestCase):
    """Test repository classes."""
    
    @patch('app.repositories.joblib.load')
    def test_faq_repository_load(self, mock_load):
        """Test FAQ repository data loading."""
        # Mock data
        mock_data = [
            {
                'question': 'Test question?',
                'answer': 'Test answer',
                'type': 'test'
            }
        ]
        mock_load.return_value = mock_data
        
        repo = FAQRepository()
        repo.load_data()
        
        faqs = repo.get_all()
        self.assertEqual(len(faqs), 1)
        self.assertEqual(faqs[0].question, 'Test question?')
    
    def test_faq_repository_get_layout(self):
        """Test FAQ layout generation."""
        with patch.object(FAQRepository, 'get_all') as mock_get_all:
            mock_get_all.return_value = [
                FAQ(question='Q1?', answer='A1', faq_type='type1'),
                FAQ(question='Q2?', answer='A2', faq_type='type2')
            ]
            
            repo = FAQRepository()
            layout = repo.get_faq_layout()
            
            self.assertIn('Q1?', layout)
            self.assertIn('A1', layout)
            self.assertIn('Q2?', layout)


if __name__ == '__main__':
    unittest.main()
