import os
import asyncio
import argparse

from dotenv import load_dotenv
from bilibili_api import Credential, Danmaku, live, user
from bilibili_api.live import LiveDanmaku, LiveRoom

from utils.room_utils import get_account_credential


async def get_same_followers(uid: int, credential: Credential) -> list:
    u = user.User(uid=uid, credential=credential)
    lists = await u.get_self_same_followers()

    for up in lists["list"]:
        print(up["uname"], end=" | ")


async def get_live_rooms(credential: Credential) -> list:
    info = await live.get_live_followers_info(True, credential=credential)
    # print(info)

    followed_rooms = info.get("rooms", [])
    recommend_rooms = info.get("recommend_rooms", [])
    return followed_rooms, recommend_rooms


async def main() -> None:
    credential = get_account_credential("DD")

    # await get_same_followers(2, credential)

    followed, recommend = await get_live_rooms(credential)

    for room in followed:
        title = room["title"]
        roomid = room["roomid"]
        uid = room["uid"]
        uname = room["uname"]
        print(roomid, title, uid, uname)
        sender = LiveRoom(roomid, credential=credential)
        await sender.send_danmaku(Danmaku("OvO"))
        await asyncio.sleep(1)

    # for room in recommend:
    #     print(room)


if __name__ == "__main__":
    asyncio.run(main())
