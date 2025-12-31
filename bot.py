import os
import time
import asyncio
import argparse
import signal
import contextlib

from dotenv import load_dotenv
from bilibili_api import Danmaku
from bilibili_api.live import LiveDanmaku, LiveRoom

from utils.room_utils import get_account_credential, get_room_id
# from ai import run_ai_conversation

from bot_helper.ratelimit_sender import RateLimitSender
from bot_helper.danmaku_listen import danmaku_listen

load_dotenv()


async def main(roomid: int, account: str):
    credential = get_account_credential(account or "DD")
    ROOMID = get_room_id(index=-1, csv_path="roomlist.csv")

    if roomid is not None:
        ROOMID = roomid

    danmaku = LiveDanmaku(ROOMID, credential=credential)
    room = LiveRoom(ROOMID, credential=credential)

    async def danmaku_sender(text: str):
        print(f"Sending danmaku: {text}")
        # await room.send_danmaku(Danmaku(text))

    ratelimit_sender = RateLimitSender(danmaku_sender, interval=1.0)
    await ratelimit_sender.start()

    danmaku_listen(danmaku, danmaku_sender)

    return danmaku, ratelimit_sender


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Bilive Bot", description="Bilibili live bot")

    parser.add_argument("-r", "--roomid", type=int)
    parser.add_argument("-a", "--account", type=str)

    args = parser.parse_args()

    danmaku, ratelimit_sender = asyncio.run(
        main(roomid=args.roomid, account=args.account)
    )

    async def _shutdown():
        await ratelimit_sender.stop()
        disconnect = getattr(danmaku, "disconnect", None)
        if callable(disconnect):
            with contextlib.suppress(Exception):
                await disconnect()
        close = getattr(danmaku, "close", None)
        if callable(close):
            with contextlib.suppress(Exception):
                result = close()
                if asyncio.iscoroutine(result):
                    await result

    async def _main():
        connect_task = asyncio.create_task(danmaku.connect())

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
