import asyncio
from spider.parse import ParseConnector, FrontItem
import spider.spider as spider


class Application:
    def __init__(
        self,
        tasks,
        parseConnector: ParseConnector = None,
    ):

        self.__parser_loop = asyncio.new_event_loop()

        if parseConnector is None:
            self.parseConnector = ParseConnector(loop=self.__parser_loop)
        else:
            self.parseConnector = parseConnector

        if isinstance(tasks, list):
            self.type = "multi_spider"
            self.tasks = {}

            for task in tasks:
                assert isinstance(task, spider.SpiderTas)
                self.tasks[task.tag] = task.get_tasks()

        elif isinstance(tasks, spider.SpiderTask):
            self.type = "single_spider"
            self.tasks = {tasks.tag: task.get_tasks()}
        else:
            raise TypeError

    async def start(self):
        self.parseConnector.start_parse()
        for r in asyncio.as_completed(self.tasks):
            completed = await r
            await self.parseConnector.add(
                FrontItem(completed.type, completed.content, completed.cb)
            )
