from typing import List, Dict
from collections.abc import Callable


class Requests:
    def __init__(
        self,
        url: str,
        method: str,
        group: List[str] = None,
        rule: Callable[[str], str] = None,
    ):
        self.root = url
        self.method = method

        if rule is not None and group is not None:
            raise TypeError

        self.group = group
        self.rule = rule
