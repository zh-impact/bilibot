import os
import time
# import asyncio

from dotenv import load_dotenv
from bilibili_api import Credential, Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom

from utils.room_utils import get_room_id

load_dotenv()

SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")

credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT)

ROOMID = get_room_id(index=-3, csv_path="roomlist.csv")

monitor = LiveDanmaku(ROOMID, credential=credential)
sender = LiveRoom(ROOMID, credential=credential)

UID = 3546845166963643


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


@monitor.on("DANMU_MSG")
async def recv(event):
    uid = event["data"]["info"][2][0]
    if uid == UID:
        return
    msg = event["data"]["info"][1]
    if msg.startswith("/"):
        cmd = msg[1:]
        result = run_command(cmd)
        if result is not None:
            await sender.send_danmaku(Danmaku(result))


# sync(monitor.connect())
