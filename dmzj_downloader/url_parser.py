__all__ = (
    'parse_dmzj_manga_name',
)

import re
from typing import Optional

NAME_PATTERNS = [
    re.compile(r'dmzj.com/info/([^.]+).'),
    re.compile(r'dmzj.com/([^/]+)'),
]


def parse_dmzj_manga_name(url: str) -> Optional[str]:
    for pattern in NAME_PATTERNS:
        result = pattern.search(url)
        if result is not None:
            return result[1]

    return None
