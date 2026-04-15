"""
localflare - A lightweight local web framework for rapid Python web development.

Fork of msgithub1/localflare with additional features and improvements.
"""

__version__ = "0.2.0"
__author__ = "localflare contributors"
__license__ = "MIT"

from .app import LocalFlare
from .request import Request
from .response import Response
from .routing import Router

__all__ = [
    "LocalFlare",
    "Request",
    "Response",
    "Router",
    "__version__",
]
