import asyncio
import argparse

from dotenv import load_dotenv
from bilibili_api import Credential, Danmaku, live_area, live
from bilibili_api.live import LiveRoom, LiveDanmaku

from utils.room_utils import get_room_id, get_account_credential

load_dotenv()


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


async def main(room_index: int, csv_path: str = "roomlist.csv", **kwargs) -> None:
    credential = get_account_credential("BOT")
    ROOMID = get_room_id(index=room_index, csv_path=csv_path)
    room = LiveRoom(ROOMID, credential=credential)

    if kwargs.get("dahanghai", False):
        await get_dahanghai(room)
    if kwargs.get("gaonengbang", False):
        await get_gaonengbang(room)

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

    parser.add_argument("-i", "--index", type=int, default=-1)
    parser.add_argument("-c", "--csv_path", type=str, default="roomlist.csv")
    parser.add_argument("-d", "--dahanghai", action="store_true", default=False)
    parser.add_argument("-g", "--gaonengbang", action="store_true", default=False)

    args = parser.parse_args()

    asyncio.run(
        main(
            room_index=args.index,
            csv_path=args.csv_path,
            dahanghai=args.dahanghai,
            gaonengbang=args.gaonengbang,
        )
    )
