import os
import asyncio
from dotenv import load_dotenv
from bilibili_api import Credential, user

load_dotenv()

SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")

credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT)


async def get_same_followers(uid: int) -> list:
    u = user.User(uid=uid, credential=credential)
    lists = await u.get_self_same_followers()
    return lists["list"]


async def main() -> None:
    lists = await get_same_followers(2)
    for up in lists:
        print(up["uname"], end=" ")


if __name__ == "__main__":
    asyncio.run(main())
