from app.app import Application
from spider.spider import SpiderTask
from spider.request import Requests
import asyncio


def p(content):

    currentConfirmedCount = content["results"][0]["currentConfirmedCount"]

    print(currentConfirmedCount)


async def main():

    news_task = await SpiderTask.init(
        tag="news",
        req=Requests("https://lab.isaaclin.cn/nCoV/api/overall", "get"),
        headers="",
        dataType="json",
        parsers=(p,),
    )

    tasks = [news_task]

    app = Application(tasks=tasks)

    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
