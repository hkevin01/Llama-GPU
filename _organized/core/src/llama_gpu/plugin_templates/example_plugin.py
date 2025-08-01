"""
Example Plugin Template
Custom plugins should inherit from this base and implement the run() method.
"""

class BasePlugin:
    def run(self, *args, **kwargs):
        raise NotImplementedError('Plugin must implement run()')

class ExamplePlugin(BasePlugin):
    def run(self, data):
        # Example processing
        return f"Processed: {data}"
