import asyncio
import aiohttp
from request import Requests
import urllib
from typing import List


class SpiderTask:
    def __init__(
        self,
        tag: str,
        req: Requests,
        headers,
        cookies=None,
        proxy=None,
        parser=None,
    ):
        self.tag = tag
        self.req = req
        self.session = aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
        )

        self.proxy = proxy

        tmp = []
        if len(req.group) != 0:
            for r in req.group:
                tmp.append(
                    asyncio.create_task(
                        aiohttp.request(
                            req.method,
                            url=urllib.parse.urljoin(req.root, r),
                        )
                    )
                )

        self.__tasks: List[asyncio.Task] = tmp
        if isinstance(parser, list) and len(parser) != len(req.group):
            raise TypeError()
        self.parser = parser

    def delete_task(self, r: int):
        self.__tasks.pop(r)

    def add_task(self, req: Requests):
        if len(req.group) != 0:
            for r in req.group:
                self.__tasks.append(
                    asyncio.create_task(
                        aiohttp.request(
                            req.method,
                            url=urllib.parse.urljoin(req.root, r),
                        )
                    )
                )

    def get_tasks(self):
        return self.tasks
