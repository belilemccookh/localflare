"""Middleware support for LocalFlare.

Provides a simple middleware chain that can be used to process
requests and responses before they reach route handlers.
"""

from functools import wraps
from typing import Callable, List, Any


class MiddlewareManager:
    """Manages a chain of middleware functions."""

    def __init__(self):
        self._middleware: List[Callable] = []

    def use(self, func: Callable) -> Callable:
        """Register a middleware function.

        Middleware functions receive (request, response, next) arguments.
        Call next() to pass control to the next middleware or route handler.

        Example:
            @app.middleware
            def logger(request, response, next):
                print(f"{request['method']} {request['path']}")
                return next()
        """
        self._middleware.append(func)
        return func

    def apply(self, handler: Callable) -> Callable:
        """Wrap a route handler with the registered middleware chain."""
        @wraps(handler)
        def wrapped(request: dict, *args, **kwargs):
            response = {"status": 200, "headers": {}, "body": None}
            index = 0
            middleware = self._middleware

            def next_middleware():
                nonlocal index
                if index < len(middleware):
                    mw = middleware[index]
                    index += 1
                    return mw(request, response, next_middleware)
                else:
                    result = handler(request, *args, **kwargs)
                    if result is not None:
                        response["body"] = result
                    return response["body"]

            return next_middleware()
        return wrapped


def cors(origins: str = "*", methods: str = "GET, POST, PUT, DELETE, OPTIONS",
         headers: str = "Content-Type") -> Callable:
    """CORS middleware factory.

    Args:
        origins: Allowed origins (default: "*")
        methods: Allowed HTTP methods
        headers: Allowed headers

    Returns:
        A middleware function that adds CORS headers to responses.
    """
    def middleware(request: dict, response: dict, next_fn: Callable) -> Any:
        response["headers"]["Access-Control-Allow-Origin"] = origins
        response["headers"]["Access-Control-Allow-Methods"] = methods
        response["headers"]["Access-Control-Allow-Headers"] = headers
        if request.get("method") == "OPTIONS":
            response["status"] = 204
            return ""
        return next_fn()
    return middleware


def request_logger(request: dict, response: dict, next_fn: Callable) -> Any:
    """Simple request logging middleware."""
    import time
    start = time.time()
    result = next_fn()
    elapsed = (time.time() - start) * 1000
    method = request.get("method", "GET")
    path = request.get("path", "/")
    status = response.get("status", 200)
    print(f"[LocalFlare] {method} {path} -> {status} ({elapsed:.1f}ms)")
    return result


def basic_auth(credentials: dict) -> Callable:
    """Basic HTTP authentication middleware factory.

    Args:
        credentials: Dict of {username: password} pairs.

    Returns:
        A middleware function that enforces basic auth.
    """
    import base64

    def middleware(request: dict, response: dict, next_fn: Callable) -> Any:
        auth_header = request.get("headers", {}).get("Authorization", "")
        if auth_header.startswith("Basic "):
            try:
                decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
                username, password = decoded.split(":", 1)
                if credentials.get(username) == password:
                    return next_fn()
            except Exception:
                pass
        response["status"] = 401
        response["headers"]["WWW-Authenticate"] = 'Basic realm="LocalFlare"'
        return "Unauthorized"
    return middleware
