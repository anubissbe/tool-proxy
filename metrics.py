"""
Metrics Collection for Ollama Agent Mode Proxy

This module provides metrics collection for monitoring the proxy's performance.
"""

# Try to import prometheus_client, but don't fail if not available
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("prometheus_client not available. Metrics will be mocked.")


# Define metrics if prometheus is available
if PROMETHEUS_AVAILABLE:
    # Request metrics
    request_count = Counter(
        'proxy_requests_total', 
        'Total requests',
        ['endpoint', 'model']
    )
    
    request_duration = Histogram(
        'proxy_request_duration_seconds', 
        'Request duration'
    )
    
    # Session metrics
    active_sessions = Gauge(
        'proxy_active_sessions', 
        'Active conversation sessions'
    )
    
    # Tool execution metrics
    tool_executions = Counter(
        'proxy_tool_executions_total', 
        'Tool executions',
        ['tool_name']
    )
    
else:
    # Define mock metrics if prometheus is not available
    class MockCounter:
        def __init__(self, name, help, labels=None):
            self.name = name
            self.help = help
            self.labels_names = labels or []
            self.value = 0
        
        def inc(self, amount=1):
            self.value += amount
            
        def labels(self, **kwargs):
            return self
    
    class MockHistogram:
        def __init__(self, name, help):
            self.name = name
            self.help = help
            self.value = 0
        
        def observe(self, amount):
            self.value = amount
        
        def time(self):
            class Timer:
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            return Timer()
    
    class MockGauge:
        def __init__(self, name, help):
            self.name = name
            self.help = help
            self.value = 0
        
        def inc(self, amount=1):
            self.value += amount
        
        def dec(self, amount=1):
            self.value -= amount
        
        def set(self, value):
            self.value = value
    
    # Create mock metrics
    request_count = MockCounter('proxy_requests_total', 'Total requests', ['endpoint', 'model'])
    request_duration = MockHistogram('proxy_request_duration_seconds', 'Request duration')
    active_sessions = MockGauge('proxy_active_sessions', 'Active conversation sessions')
    tool_executions = MockCounter('proxy_tool_executions_total', 'Tool executions', ['tool_name'])