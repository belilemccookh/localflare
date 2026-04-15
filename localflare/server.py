"""Core server module for localflare.

Provides the main LocalFlare server class that wraps Flask and exposes
local services over HTTP with optional tunnel support.
"""

import os
import socket
import threading
from typing import Callable, Optional

from flask import Flask


class LocalFlare:
    """A lightweight local web server with easy route registration.

    Example::

        from localflare import LocalFlare

        app = LocalFlare()

        @app.route("/")
        def index():
            return "Hello, world!"

        app.run()
    """

    def __init__(
        self,
        name: str = "localflare",
        host: str = "127.0.0.1",  # Changed from 0.0.0.0 — bind to localhost only by default for safety
        port: int = 5000,
        debug: bool = False,
        static_folder: Optional[str] = None,
        template_folder: Optional[str] = None,
    ):
        """
        Initialize the LocalFlare server.

        Args:
            name: Application name, used as Flask's import_name.
            host: Host address to bind to. Defaults to 127.0.0.1 (localhost only).
            port: Port number to listen on.
            debug: Enable Flask debug mode.
            static_folder: Path to the static files folder.
            template_folder: Path to the templates folder.
        """
        self.host = host
        self.port = port
        self.debug = debug
        self._thread: Optional[threading.Thread] = None

        flask_kwargs = {"import_name": name}
        if static_folder:
            flask_kwargs["static_folder"] = static_folder
        if template_folder:
            flask_kwargs["template_folder"] = template_folder

        self.app = Flask(**flask_kwargs)
        # Disable default Flask banner for cleaner output
        import logging
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.WARNING)

    # ------------------------------------------------------------------
    # Route helpers
    # ------------------------------------------------------------------

    def route(self, path: str, **kwargs):
        """Decorator to register a URL route, mirroring Flask's @app.route."""
        return self.app.route(path, **kwargs)

    def add_route(self, path: str, view_func: Callable, **kwargs):
        """Programmatically add a route without using a decorator."""
        endpoint = kwargs.pop("endpoint", view_func.__name__)
        self.app.add_url_rule(path, endpoint=endpoint, view_func=view_func, **kwargs)

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = None,
        threaded: bool = True,
    ):
        """Start the server (blocking).

        Args:
            host: Override the instance host.
            port: Override the instance port.
            debug: Override the instance debug flag.
            threaded: Handle each request in a separate thread.
       