import os
import csv
from typing import List

from dotenv import load_dotenv
from bilibili_api import Credential

load_dotenv()


def get_account_credential(account_prefix: str) -> Credential:
    return Credential(
        sessdata=os.getenv(f"{account_prefix}:SESSDATA"),
        bili_jct=os.getenv(f"{account_prefix}:BILI_JCT"),
    )


def check_credential(account_prefix: str) -> bool:
    return get_account_credential(account_prefix).check_refresh()


def refresh_credential(account_prefix: str) -> None:
    get_account_credential(account_prefix).refresh()


def load_room_ids(csv_path: str = "roomlist.csv") -> List[int]:
    room_ids: List[int] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            # print(row)
            room_ids.append(int(row[0]))
    return room_ids


def get_room_id(index: int = -3, csv_path: str = "roomlist.csv") -> int:
    room_ids = load_room_ids(csv_path=csv_path)
    return room_ids[index]
