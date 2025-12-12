import os
import asyncio
from dotenv import load_dotenv
from bilibili_api import Credential, Danmaku, live_area, live
from bilibili_api.live import LiveRoom, LiveDanmaku

from utils.room_utils import get_room_id

load_dotenv()

SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")

credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT)

ROOMID = get_room_id(index=-3, csv_path="roomlist.csv")


async def get_dahanghai(sender: LiveRoom) -> None:
    info = await sender.get_dahanghai()
    # print(info)
    print("-" * 30)
    top3 = info["top3"]
    all = top3 + info["list"]
    for i in all:
        print(i["rank"], i["uid"], i["username"])
    print("-" * 30)


async def get_gaonengbang(sender: LiveRoom) -> None:
    info = await sender.get_gaonengbang()
    print(info)
    online_num = info["onlineNum"]
    print(f"当前在线人数: {online_num}")
    print("-" * 30)
    for i in info["OnlineRankItem"]:
        print(i["userRank"], i["uid"], i["name"])
    print("-" * 30)


async def main():
    sender = LiveRoom(ROOMID, credential=credential)
    # await get_dahanghai(sender)
    # await get_gaonengbang(sender)
    # await sender.send_danmaku(Danmaku("OvO"))

    # await live_area.fetch_live_area_data()
    # main_area, sub_area = live_area.get_area_info_by_name("网游")
    # print(main_area)

    info = await live.get_live_followers_info(False, credential=credential)
    print(info)


if __name__ == "__main__":
    asyncio.run(main())
