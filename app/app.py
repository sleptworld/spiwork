import asyncio
from spider.parse import ParseConnector, EndOfItmeLines
import spider.spider as spider


class Application:
    def __init__(
        self,
        tasks,
        parseConnector: ParseConnector = None,
    ):

        self.__parser_loop = asyncio.new_event_loop()

        if parseConnector is None:
            self.parseConnector = ParseConnector()
        else:
            self.parseConnector = parseConnector

        if isinstance(tasks, list):
            self.type = "multi_spider"
            self.tasks = {}

            for task in tasks:
                assert isinstance(task, spider.SpiderTask)
                self.tasks[task.tag] = task.create_tasks()

        elif isinstance(tasks, spider.SpiderTask):
            self.type = "single_spider"
            self.tasks = {tasks.tag: tasks.create_tasks()}
        else:
            raise TypeError

    def __creat_tasks(self):
        tasks = []
        for key in self.tasks.keys():
            item = self.tasks[key]

            tasks.append(*(item))

        return tasks

    async def start(self):
        self.parseConnector.start_parse()
        for r in asyncio.as_completed(self.__creat_tasks()):
            completed = await r
            self.parseConnector.add(completed)

        self.parseConnector.add(EndOfItmeLines())
        self.parseConnector.queue.join()
        self.parseConnector.process.join()
