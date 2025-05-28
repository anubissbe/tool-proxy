import asyncio
import logging
from typing import Dict, Any, List
import aiohttp
import json
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MCP Server')

class MCPServer:
    def __init__(self, 
                 search_api_key: str = None, 
                 proxy_url: str = None):
        """
        Initialize MCP Server with search and proxy capabilities
        
        :param search_api_key: API key for search service
        :param proxy_url: Optional proxy URL for internet searches
        """
        load_dotenv()
        
        # Search API Configuration
        self.search_api_key = search_api_key or os.getenv('SEARCH_API_KEY')
        self.search_endpoint = os.getenv(
            'SEARCH_ENDPOINT', 
            'https://www.googleapis.com/customsearch/v1'
        )
        self.proxy_url = proxy_url or os.getenv('SEARCH_PROXY')
        
        # Caching and rate limiting
        self.search_cache: Dict[str, Any] = {}
        self.rate_limit_window = 60  # seconds
        self.max_searches_per_window = 10
        
    async def search_internet(self, 
                               query: str, 
                               num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform internet search with optional proxy
        
        :param query: Search query
        :param num_results: Number of results to return
        :return: List of search results
        """
        # Check cache first
        if query in self.search_cache:
            return self.search_cache[query]
        
        try:
            # Prepare search parameters
            params = {
                'key': self.search_api_key,
                'cx': os.getenv('SEARCH_CX'),  # Custom Search Engine ID
                'q': query,
                'num': num_results
            }
            
            # Configure proxy if available
            proxy = self.proxy_url if self.proxy_url else None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.search_endpoint, 
                    params=params, 
                    proxy=proxy
                ) as response:
                    if response.status != 200:
                        logger.error(f"Search failed: {response.status}")
                        return []
                    
                    results = await response.json()
                    
                    # Extract and format results
                    formatted_results = [
                        {
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        } 
                        for item in results.get('items', [])
                    ]
                    
                    # Cache results
                    self.search_cache[query] = formatted_results
                    return formatted_results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def process_tool_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process tool requests from language models
        
        :param request: Tool request dictionary
        :return: Tool execution result
        """
        tool_name = request.get('tool_name')
        params = request.get('parameters', {})
        
        tool_handlers = {
            'internet_search': self.search_internet,
            # Add more tool handlers here
        }
        
        handler = tool_handlers.get(tool_name)
        if not handler:
            return {
                'error': f'Unknown tool: {tool_name}',
                'status': 'failure'
            }
        
        try:
            result = await handler(**params)
            return {
                'result': result,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                'error': str(e),
                'status': 'failure'
            }
    
    async def start_server(self, host: str = '0.0.0.0', port: int = 8765):
        """
        Start WebSocket server for MCP communication
        
        :param host: Server host
        :param port: Server port
        """
        server = await asyncio.start_server(
            self.handle_client, 
            host, 
            port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f'Serving on {addr}')
        
        async with server:
            await server.serve_forever()
    
    async def handle_client(self, reader: asyncio.StreamReader, 
                             writer: asyncio.StreamWriter):
        """
        Handle individual client connections
        
        :param reader: Stream reader
        :param writer: Stream writer
        """
        addr = writer.get_extra_info('peername')
        logger.info(f'Received connection from {addr}')
        
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                try:
                    request = json.loads(data.decode())
                    response = await self.process_tool_request(request)
                    writer.write(json.dumps(response).encode())
                    await writer.drain()
                except json.JSONDecodeError:
                    logger.error('Invalid JSON request')
                except Exception as e:
                    logger.error(f'Request processing error: {e}')
        
        except asyncio.CancelledError:
            logger.info('Connection closed')
        finally:
            writer.close()
            await writer.wait_closed()

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize and start MCP Server
    mcp_server = MCPServer()
    await mcp_server.start_server()

if __name__ == '__main__':
    asyncio.run(main())