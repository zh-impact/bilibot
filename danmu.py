import asyncio
import contextlib
import os
import signal
from dotenv import load_dotenv
from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku

from utils.room_utils import get_room_id

load_dotenv()

SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")

credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT)

ROOMID = get_room_id(index=0, csv_path="roomlist.csv")

room = LiveDanmaku(ROOMID, credential=credential)


@room.on("DANMU_MSG")
async def on_danmaku(event):
    print("-" * 30)
    print(event["data"]["info"][2][1], event["data"]["info"][1])
    print("-" * 30)


@room.on("SEND_GIFT")
async def on_gift(event):
    print("-" * 30)
    print(event)
    print("-" * 30)


if __name__ == "__main__":

    async def _shutdown():
        disconnect = getattr(room, "disconnect", None)
        if callable(disconnect):
            with contextlib.suppress(Exception):
                await disconnect()
        close = getattr(room, "close", None)
        if callable(close):
            with contextlib.suppress(Exception):
                result = close()
                if asyncio.iscoroutine(result):
                    await result

    async def _main():
        connect_task = asyncio.create_task(room.connect())

        loop = asyncio.get_running_loop()
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(signal.SIGINT, connect_task.cancel)

        try:
            await connect_task
        except asyncio.CancelledError:
            pass
        finally:
            await _shutdown()

    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\n已退出")
