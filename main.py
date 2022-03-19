from app import Application
from spider.spider import SpiderTask
from spider.request import Requests
import asyncio


def main():
    tasks = [
        SpiderTask(
            "news",
            Requests(
                "http://www.baidu.com",
                [],
                "get",
                {},
            ),
        ),
    ]

    app = Application(tasks=tasks)
    asyncio.run(app.start())


if __name__ == "__main__":
    main()
