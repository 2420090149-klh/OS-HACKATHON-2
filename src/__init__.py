"""Package initializer for local src package used in tests.

Having an explicit __init__ ensures the local `src` package is preferred
over any conflicting top-level `src` modules on sys.path during testing.
"""

__all__ = ["analyzer"]
