import os
import asyncio
from dotenv import load_dotenv
from bilibili_api import Credential, user

from utils.room_utils import get_room_id, get_account_credential


async def get_same_followers(uid: int) -> list:
    credential = get_account_credential("BOT")
    u = user.User(uid=uid, credential=credential)
    lists = await u.get_self_same_followers()

    for up in lists["list"]:
        print(up["uname"], end=" | ")


async def main() -> None:
    await get_same_followers(2)


if __name__ == "__main__":
    asyncio.run(main())
