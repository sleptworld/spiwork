from collections.abc import Callable
from multiprocessing import Process
from multiprocessing import JoinableQueue, Pipe


class OutPutItem:
    def __init__(self):
        pass


class FrontItem:
    def __init__(
        self,
        status_code: int,
        contentType: str,
        content: str,
        parserFunction: Callable[[str], OutPutItem],
    ):
        self.type = contentType
        self.content = content
        self.parserFunction = parserFunction
        self.status_code = status_code


class EndOfItmeLines(FrontItem):
    def __init__(
        self,
        status_code=None,
        contentType=None,
        content=None,
        parserFunction=None,
    ):
        super().__init__(status_code, contentType, content, parserFunction)


def parsing(queue, conn):
    while True:

        try:
            item: FrontItem = queue.get()

            if isinstance(item, EndOfItmeLines):
                break

            item.parserFunction(item.content)

        except:
            print("something wrong")

        finally:
            queue.task_done()


class ParseConnector:
    def __init__(self, process=None, conn=None, queue=None):
        self.process = process
        self.conn = conn
        self.queue = queue
        self.finished = False

    def __del__(self):
        self.conn.close()
        self.process.close()

    def add(self, item: FrontItem):
        self.queue.put(item)
        if isinstance(item, EndOfItmeLines):
            self.finished = True

    def start_parse(self):

        if self.conn is None:
            parent_conn, child_conn = Pipe()
            self.conn = parent_conn

        if self.queue is None:
            self.queue = JoinableQueue()

        if self.process is None:
            self.process = Process(
                target=parsing,
                args=(
                    self.queue,
                    child_conn,
                ),
            )
            self.process.daemon = True

            self.process.start()

    def is_parsing(self):
        return self.finished
