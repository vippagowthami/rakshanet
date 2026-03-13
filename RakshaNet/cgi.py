"""
Minimal shim for the stdlib `cgi` module providing `parse_header`.
This fixes missing `cgi` in the system Python used here (3.14).
Only implements what's needed by Django (`parse_header`).
"""
from typing import Tuple, Dict


def parse_header(value: str) -> Tuple[str, Dict[str, str]]:
    """Parse a Content-Type like header into a main value and parameters.

    Example: 'text/html; charset=utf-8' -> ('text/html', {'charset': 'utf-8'})
    This is a minimal implementation sufficient for Django's use.
    """
    if not value:
        return '', {}
    parts = value.split(';')
    main = parts[0].strip()
    params: Dict[str, str] = {}
    for param in parts[1:]:
        if '=' in param:
            k, v = param.split('=', 1)
            k = k.strip().lower()
            v = v.strip().strip('"')
            params[k] = v
    return main, params
