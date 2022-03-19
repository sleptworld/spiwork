import threading
import asyncio
from collections.abc import Callable


class OutPutItem:
    def __init__(self):
        pass


class FrontItem:
    def __init__(
        self,
        contentType: str,
        content: str,
        parserFunction: Callable[[str], OutPutItem],
    ):
        self.type = contentType
        self.content = content
        self.parserFunction = parserFunction


class ParseConnector:
    def __init__(self, loop, tr=None):
        self.__queue = asyncio.Queue()
        self.__loop = loop
        if tr is None:
            self.__threading = threading.Thread(
                target=__NewTr,
                args=(loop,),
            )
            self.__threading.daemon = True

        else:
            self.__threading = tr

        self.__threading.start()

    async def add(self, item: FrontItem):
        await self.__queue.put(item)

    async def parsing(self):
        while True:
            item: FrontItem = await self.__queue.get()
            item.parserFunction(item.content)
            self.__queue.task_done()
        await self.__queue.join()

    def start_parse(self):
        asyncio.run_coroutine_threadsafe(self.parsing(), self.__loop)


def __NewTr(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
