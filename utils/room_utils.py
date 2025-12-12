import csv
from typing import List


def load_room_ids(csv_path: str = "roomlist.csv") -> List[int]:
    room_ids: List[int] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)
            room_ids.append(int(row[0]))
    return room_ids


def get_room_id(index: int = -3, csv_path: str = "roomlist.csv") -> int:
    room_ids = load_room_ids(csv_path=csv_path)
    return room_ids[index]
