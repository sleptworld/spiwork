import asyncio
import aiohttp
from .request import Requests
from .parse import FrontItem
import urllib
from enum import Enum, auto
from typing import Tuple
from collections.abc import Callable


class SpiderTaskStatus(Enum):
    INIT = auto()
    PROCESSING = auto()
    SUCCESSED = auto()
    FAILED = auto()


def test(content):
    print(content)


class SpiderTask:
    def __init__(
        self,
        tag: str,
        req: Requests,
        session: aiohttp.ClientSession,
        parsers: Tuple[Callable[[str], str]],
        dataType: str,
    ):
        self.tag = tag
        self.req = req
        self.session = session
        self.__tasks = None
        self.__wrong_list = []
        self.__parsers = parsers
        self.status = SpiderTaskStatus.INIT
        self.finished = 0
        self.dataType = dataType

    @classmethod
    async def init(
        self,
        tag: str,
        req: Requests,
        headers,
        parsers=(test,),
        dataType: str = "text",
        cookies=None,
        proxy=None,
    ):
        session = aiohttp.ClientSession(headers=headers)
        return SpiderTask(
            tag,
            req,
            session,
            parsers=parsers,
            dataType=dataType,
        )

    def create_tasks(self):
        async def rq(path: str, parser):
            async with self.session.request(self.req.method, path) as response:
                if response.status != 200:
                    await self.task_done(failed=True, path=path)
                    return FrontItem(
                        response.status,
                        None,
                        None,
                        None,
                    )
                else:
                    await self.task_done()

                    if self.dataType == "text":
                        c = await response.text()
                    elif self.dataType == "json":
                        c = await response.json()
                    else:
                        c = await response.read()

                    return FrontItem(
                        200,
                        response.content_type,
                        c,
                        parser,
                    )

        if self.__tasks is None:
            tmp = []

            if self.req.group is not None:
                if len(self.__parsers) == 1:
                    for r in self.req.group:
                        tmp.append(
                            rq(urllib.parse.urljoin(self.req.root, r)),
                            self.__parsers[0],
                        )
                else:
                    for r, parser in zip(self.req.group, self.__parsers):
                        tmp.append(
                            rq(urllib.parse.urljoin(self.req.root, r)),
                            parser,
                        )
            elif self.req.rule is not None:
                if len(self.__parsers) == 1:
                    for r in self.req.rule(self.req.root):
                        tmp.append(self.__parsers[0])
                else:
                    for r, parser in zip(self.req.group, self.__parsers):
                        for r in self.req.rule(self.req.root):
                            tmp.append(parser)

            else:
                assert len(self.__parsers) == 1
                tmp.append(rq(self.req.root, self.__parsers[0]))

            self.__tasks = tmp
            assert len(self.__parsers) == 1 or len(self.__parsers) == len(self.__tasks)
        return self.__tasks

    async def close(self):
        await self.session.close()

    async def task_done(self, failed: bool = False, path: str = None):
        if failed:
            assert path is not None
            self.add_wrong_item(path)
        self.finished += 1

        if self.finished == len(self.__tasks):
            await self.close()

            if len(self.__wrong_list) != 0:
                self.status = SpiderTaskStatus.FAILED
            else:
                self.status = SpiderTaskStatus.SUCCESSED
        else:
            self.status = SpiderTaskStatus.PROCESSING

        print(self.status)

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

    def add_wrong_item(self, path: str):
        self.__wrong_list.append(path)

    def get_wrong_item(self):
        return self.__wrong_list

    def get_tasks(self):
        return self.tasks
