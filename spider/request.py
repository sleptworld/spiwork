from typing import List, Dict


class Requests:
    def __init__(
        self,
        url: str,
        group: List[str],
        method: str,
    ):
        self.root = url
        self.method = method
        self.group = group
