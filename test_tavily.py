import pytest
from unittest.mock import Mock, patch
from agent import ResearchAgent
from models import ResearchReport

class TestResearchAgent:
    
    @patch('agent.TavilyClient')
    @patch('agent.ChatOpenAI')
    def test_agent_initialization(self, mock_llm, mock_tavily):
        """Test agent initialization."""
        agent = ResearchAgent()
        assert agent is not None
        assert agent.llm is not None
        assert agent.tavily is not None
    
    @patch('agent.TavilyClient')
    @patch('agent.ChatOpenAI')
    def test_search_web(self, mock_llm, mock_tavily):
        """Test web search functionality."""
        # Mock search response
        mock_tavily.return_value.search.return_value = {
            'results': [
                {'title': 'Test Title', 'content': 'Test content here'}
            ]
        }
        
        agent = ResearchAgent()
        result = agent._search_web("test query")
        
        assert "Test Title" in result
        assert "Test content" in result
    
    @patch('agent.TavilyClient')
    @patch('agent.ChatOpenAI')
    def test_research(self, mock_llm, mock_tavily):
        """Test research functionality."""
        # Mock the agent's research
        mock_llm.return_value.invoke.return_value = {
            'output': 'Test output'
        }
        
        agent = ResearchAgent()
        
        # Mock the parser
        with patch.object(agent, 'parser') as mock_parser:
            mock_parser.parse.return_value = ResearchReport(
                title="Test Report",
                introduction="Test introduction",
                key_findings=["Finding 1", "Finding 2"],
                conclusion="Test conclusion"
            )
            
            result = agent.research("test topic")
            assert result['success'] is True
            assert 'report' in result

class TestCache:
    @patch('cache.redis.Redis')
    def test_cache_get_set(self, mock_redis):
        """Test cache functionality."""
        from cache import RedisCache
        
        cache = RedisCache()
        cache.enabled = True
        cache.client = mock_redis
        
        # Test set
        test_data = {'key': 'value'}
        cache.set("test", test_data)
        mock_redis.setex.assert_called_once()
        
        # Test get
        mock_redis.get.return_value = '{"key": "value"}'
        result = cache.get("test")
        assert result == test_data