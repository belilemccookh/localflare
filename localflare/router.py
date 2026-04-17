"""Router module for localflare — handles URL pattern matching and route registration."""

import re
from typing import Callable, Dict, List, Optional, Tuple


class Route:
    """Represents a single route with a URL pattern, HTTP method, and handler."""

    def __init__(self, path: str, method: str, handler: Callable):
        self.path = path
        self.method = method.upper()
        self.handler = handler
        self.pattern, self.param_names = self._compile(path)

    def _compile(self, path: str) -> Tuple[re.Pattern, List[str]]:
        """Convert a path like /user/<id> into a regex pattern and extract param names."""
        param_names = []
        # Replace <param> with named capture groups
        def replace_param(match):
            name = match.group(1)
            param_names.append(name)
            return r'([^/]+)'

        pattern_str = re.sub(r'<([^>]+)>', replace_param, path)
        pattern_str = f'^{pattern_str}$'
        return re.compile(pattern_str), param_names

    def match(self, path: str, method: str) -> Optional[Dict[str, str]]:
        """Try to match a request path and method. Returns path params dict or None."""
        if self.method != method.upper() and self.method != 'ANY':
            return None
        m = self.pattern.match(path)
        if m is None:
            return None
        return dict(zip(self.param_names, m.groups()))


class Router:
    """Manages a collection of routes and resolves incoming requests."""

    def __init__(self):
        self._routes: List[Route] = []

    def add_route(self, path: str, method: str, handler: Callable) -> None:
        """Register a new route."""
        route = Route(path, method, handler)
        self._routes.append(route)

    def route(self, path: str, methods: List[str] = None):
        """Decorator to register a handler for one or more HTTP methods."""
        if methods is None:
            methods = ['GET']

        def decorator(func: Callable) -> Callable:
            for method in methods:
                self.add_route(path, method, func)
            return func

        return decorator

    def resolve(self, path: str, method: str) -> Tuple[Optional[Callable], Dict[str, str]]:
        """Find a matching handler and extract URL parameters.

        Returns:
            (handler, params) tuple, or (None, {}) if no match found.
        """
        for route in self._routes:
            params = route.match(path, method)
            if params is not None:
                return route.handler, params
        return None, {}

    def get_routes(self) -> List[Dict]:
        """Return a list of registered routes for debugging or introspection."""
        return [
            {
                'path': r.path,
                'method': r.method,
                'handler': r.handler.__name__,
            }
            for r in self._routes
        ]
