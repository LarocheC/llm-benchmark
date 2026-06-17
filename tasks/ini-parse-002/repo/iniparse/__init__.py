"""A tiny INI parser: ``[section]`` headers and ``key = value`` lines."""
from .parser import parse_ini

__all__ = ["parse_ini"]
