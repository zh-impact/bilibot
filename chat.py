import os
import time
import asyncio
import signal
import contextlib

from dotenv import load_dotenv
from bilibili_api import Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom

from utils.room_utils import get_account_credential, get_room_id

load_dotenv()


def run_command(cmd: str):
    available_commands = ("活力大湾区", "天王盖地虎", "time", "")
    if cmd in available_commands:
        if cmd == "活力大湾区":
            return "美丽新广州"
        elif cmd == "天王盖地虎":
            return "宝塔镇河妖"
        elif cmd == "time":
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        elif cmd == "":
            return ""
    return None


def main():
    credential = get_account_credential("BOT")
    ROOMID = get_room_id(index=-1, csv_path="roomlist.csv")
    BOT_UID = os.getenv("BOT:UID")
    room = LiveDanmaku(ROOMID, credential=credential)
    sender = LiveRoom(ROOMID, credential=credential)

    @room.on("SEND_GIFT")
    async def on_gift(event):
        print("-" * 30)
        print(event)
        print("-" * 30)

    @room.on("DANMU_MSG")
    async def recv(event):
        print("-" * 30)
        print(event["data"]["info"][2][1], event["data"]["info"][1])
        print("-" * 30)

        uid = event["data"]["info"][2][0]
        if uid == BOT_UID:
            return

        msg = event["data"]["info"][1]
        if msg.startswith("/"):
            cmd = msg[1:]
            result = run_command(cmd)
            if result is not None:
                await sender.send_danmaku(Danmaku(result))

    return room


if __name__ == "__main__":
    room = main()

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
