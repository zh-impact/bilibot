import asyncio
import argparse
import json
import os

from dotenv import load_dotenv
from bilibili_api import Credential, Danmaku, live_area, live, user
from bilibili_api.live import LiveRoom, LiveDanmaku

from utils.room_utils import get_room_id, get_account_credential


async def get_dahanghai(room: LiveRoom) -> None:
    info = await room.get_dahanghai()
    # print(info)
    print("-" * 15, "大航海", "-" * 15)
    top3 = info["top3"]
    all = top3 + info["list"]
    for i in all:
        print(i["rank"], i["uid"], i["username"])


async def get_gaonengbang(room: LiveRoom) -> None:
    info = await room.get_gaonengbang()
    # print(info)
    print("-" * 15, "高能榜", "-" * 15)
    online_num = info["onlineNum"]
    print(f"当前在线人数: {online_num}")
    print("-" * 30)
    for i in info["OnlineRankItem"]:
        print(i["userRank"], i["uid"], i["name"])


async def get_gift(room_id: int, filename: str = "gift.json") -> None:
    gift = await live.get_gift_config(room_id=room_id)
    giftstr = json.dumps(gift, indent=2, ensure_ascii=False)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(giftstr)


# 31036 小花花 100
# 30869 心动卡 100
# 20002 flag 200

GIFTS = {"31036": 100, "30869": 100, "20002": 200}


async def send_gift(room: LiveRoom, gift_id: str, price: int):
    await room.send_gift_gold(
        uid=437055093, gift_id=gift_id, gift_num=1, price=price, storm_beat_id=0
    )


async def send_emoticon(room: LiveRoom, emoticon_code: str):
    await room.send_emoticon(emoticon=Danmaku(emoticon_code))


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


async def main(
    room_index: int,
    csv_path: str = "roomlist.csv",
    roomid: int = None,
    account: str = None,
    **kwargs,
) -> None:
    credential = get_account_credential(account or "BOT")
    ROOMID = get_room_id(index=room_index, csv_path=csv_path)
    BOT_UID = os.getenv("BOT:UID")

    if roomid is not None:
        ROOMID = roomid
    danmaku = LiveDanmaku(ROOMID, credential=credential)
    room = LiveRoom(ROOMID, credential=credential)

    if kwargs.get("dahanghai", False):
        await get_dahanghai(room)
    if kwargs.get("gaonengbang", False):
        await get_gaonengbang(room)

    room_info = await room.get_room_play_info_v2()
    print(room_info)

    # await get_same_followers(2, credential)

    # followed, recommend = await get_live_rooms(credential)

    # for room in followed:
    #     title = room["title"]
    #     roomid = room["roomid"]
    #     uid = room["uid"]
    #     uname = room["uname"]
    #     print(roomid, title, uid, uname)
    #     sender = LiveRoom(roomid, credential=credential)
    #     await sender.send_danmaku(Danmaku("OvO"))
    #     await asyncio.sleep(1)

    # print(await room.get_room_id())
    # print(await room.get_room_info())
    # print(await room.get_emoticons())
    # await send_emoticon(room, "official_331")
    # await asyncio.sleep(1)
    # await send_emoticon(room, "official_332")
    # await asyncio.sleep(1)
    # await send_emoticon(room, "upower_[CHIIKAWA来了_悠哉]")
    # await asyncio.sleep(1)
    # await room.send_emoticon(emoticon=Danmaku("official_332"))
    # await room.send_danmaku(Danmaku("[dog]666"))

    # for i in range(10):
    #     await send_gift(room, gift_id="30869", price=100)
    #     await asyncio.sleep(1)
    #     await send_gift(room, gift_id="20002", price=200)
    #     await asyncio.sleep(1)

    # await get_gift(room_id=ROOMID, filename="baicai.json")

    # com_gift = await room.get_gift_common()
    # gstr = json.dumps(com_gift, indent=2, ensure_ascii=False)
    # with open("com-gift.json", "w", encoding="utf-8") as f:
    #     f.write(gstr)

    # gift = await live.get_gift_config()
    # jsonstr = json.dumps(gift, indent=2, ensure_ascii=False)
    # with open("gift.json", "w", encoding="utf-8") as f:
    #     f.write(jsonstr)

    # await room.send_danmaku(Danmaku("OvO"))

    # await live_area.fetch_live_area_data()
    # main_area, sub_area = live_area.get_area_info_by_name("网游")
    # print(main_area)

    # info = await live.get_live_followers_info(False, credential=credential)
    # print(info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="bilibot debug", description="Debug bilibili api"
    )

    parser.add_argument("-a", "--account", type=str)
    parser.add_argument("-c", "--csv_path", type=str, default="roomlist.csv")
    parser.add_argument("-d", "--dahanghai", action="store_true", default=False)
    parser.add_argument("-g", "--gaonengbang", action="store_true", default=False)
    parser.add_argument("-i", "--index", type=int, default=1)
    parser.add_argument("-r", "--roomid", type=int)

    args = parser.parse_args()

    asyncio.run(
        main(
            room_index=args.index,
            csv_path=args.csv_path,
            dahanghai=args.dahanghai,
            gaonengbang=args.gaonengbang,
            roomid=args.roomid,
            account=args.account,
        )
    )
