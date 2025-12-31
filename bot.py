import os
import time
import asyncio
import argparse
import signal
import contextlib

from dotenv import load_dotenv
from bilibili_api import Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom

from utils.room_utils import get_account_credential, get_room_id
from utils.bot_msg import get_welcome_msg
# from ai import run_ai_conversation

from bot_helper.ratelimit_sender import RateLimitSender

load_dotenv()

WAKE_WORD = "小坤小坤"


def run_command(msg: str):
    cmd = msg[len(WAKE_WORD) :]
    print(cmd)
    available_commands = ("你好", "天王盖地虎", "time")
    if cmd in available_commands:
        if cmd == "你好":
            return "你好"
        elif cmd == "天王盖地虎":
            return "宝塔镇河妖"
        elif cmd == "time":
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    else:
        # return run_ai_conversation(cmd)
        return None


def inspect_event(event, name: str):
    print("-" * 30, name or "Event", "-" * 30)
    print(event)
    print("-" * 30)


def main(roomid: int, account: str):
    credential = get_account_credential(account or "DD")
    ROOMID = get_room_id(index=-1, csv_path="roomlist.csv")
    BOT_UID = os.getenv("BOT:UID")

    if roomid is not None:
        ROOMID = roomid

    danmaku = LiveDanmaku(ROOMID, credential=credential)
    sender = LiveRoom(ROOMID, credential=credential)

    async def danmaku_sender(text: str):
        await sender.send_danmaku(Danmaku(text))

    ratelimit_sender = RateLimitSender(danmaku_sender, interval=1.0)
    await ratelimit_sender.start()

    @danmaku.on("GUARD_BUY")
    async def on_guard_buy(event):
        inspect_event(event, "GUARD_BUY")
        data = event["data"]["data"]
        name = data["username"]
        num = data["num"]
        gift_name = data["gift_name"]
        print(f"{name} 开通了 {num} {gift_name}")
        msg = f"感谢 {name} 开通了 {gift_name}"
        await ratelimit_sender.send(msg)

    @danmaku.on("COMBO_SEND")
    async def on_combo_send(event):
        inspect_event(event, "COMBO_SEND")

    @danmaku.on("SUPER_CHAT_MESSAGE")
    async def on_super_chat(event):
        inspect_event(event, "SUPER_CHAT_MESSAGE")

    @danmaku.on("GIFT_STAR_PROCESS")
    async def on_gift_star_process(event):
        inspect_event(event, "GIFT_STAR_PROCESS")

    @danmaku.on("SPECIAL_GIFT")
    async def on_special_gift(event):
        inspect_event(event, "SPECIAL_GIFT")

    @danmaku.on("LIKE_INFO_V3_CLICK")
    async def on_like_info_v3_click(event):
        inspect_event(event, "LIKE_INFO_V3_CLICK")
        data = event["data"]["data"]
        name = data["uname"]
        print(f"{name} 点赞了直播间")
        await ratelimit_sender.send(f"感谢 {name} 的点赞")

    @danmaku.on("WARNING")
    async def on_warning(event):
        inspect_event(event, "WARNING")

    @danmaku.on("SEND_GIFT")
    async def on_gift(event):
        print("-" * 30)
        # inspect_event(event, "SEND_GIFT")
        data = event["data"]["data"]
        name = data["uname"]
        action = data["action"]
        num = data["num"]
        giftName = data["giftName"]
        print(f"{name} {action} {num} {giftName}")
        msg = f"感谢 {name} {action}的{num}个{giftName}"
        await ratelimit_sender.send(msg)
        print("-" * 30)

    @danmaku.on("DANMU_MSG")
    async def recv(event):
        print("-" * 30)
        info = event["data"]["info"]
        msg = info[1]
        print(f"{info[2][1]}: {msg}")
        print("-" * 30)

        uid = info[2][0]
        if uid == BOT_UID:
            return

        print(msg.startswith(WAKE_WORD), uid, BOT_UID)
        if msg.startswith(WAKE_WORD):
            result = run_command(msg)
            if result is not None:
                await ratelimit_sender.send(result)

    @danmaku.on("INTERACT_WORD_V2")
    async def on_interact_word(event):
        print("-" * 30, "INTERACT_WORD_V2", "-" * 30)
        decode_message = event["data"]["data"]["pb_decode_message"]
        if decode_message == "success":
            user_name = event["data"]["data"]["pb_decoded"]["uname"]
            user_info = event["data"]["data"]["pb_decoded"].get("user_info", {})
            guard_info = user_info.get("guard", {})
            level = guard_info.get("level", 0)
            print(f"{user_name} 进入直播间")
            await ratelimit_sender.send(get_welcome_msg(user_name, level))
            print("-" * 30)
        else:
            print("Decode failed")
            print("-" * 30)

    return danmaku


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Bilive Bot", description="Bilibili live bot")

    parser.add_argument("-r", "--roomid", type=int)
    parser.add_argument("-a", "--account", type=str)

    args = parser.parse_args()

    room = main(roomid=args.roomid, account=args.account)

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
