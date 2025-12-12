import os
from dotenv import load_dotenv
from bilibili_api import Credential, sync
from bilibili_api.live import LiveDanmaku

from utils.room_utils import get_room_id

load_dotenv()

SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")

credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT)

ROOMID = get_room_id(index=-3, csv_path="roomlist.csv")

room = LiveDanmaku(ROOMID, credential=credential)


@room.on("DANMU_MSG")
async def on_danmaku(event):
    print("-" * 30)
    print(event["data"]["info"][1])
    print("-" * 30)


@room.on("SEND_GIFT")
async def on_gift(event):
    print("-" * 30)
    print(event)
    print("-" * 30)


if __name__ == "__main__":
    sync(room.connect())
