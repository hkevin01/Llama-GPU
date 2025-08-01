"""
Plugin Event Hooks Utility
Provides event hook registration and dispatch for plugin lifecycle events.
"""
from typing import Callable, Dict, List

class PluginEventManager:
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {
            'pre_load': [],
            'post_load': [],
            'pre_unload': [],
            'post_unload': [],
            'pre_reload': [],
            'post_reload': []
        }

    def register_hook(self, event: str, func: Callable) -> None:
        if event in self.hooks:
            self.hooks[event].append(func)

    def dispatch(self, event: str, *args, **kwargs) -> None:
        for func in self.hooks.get(event, []):
            func(*args, **kwargs)

