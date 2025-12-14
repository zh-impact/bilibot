import os
from time import monotonic

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    Vertical,
    VerticalScroll,
    VerticalGroup,
)
from textual.widgets import Footer, Header, Button, Label, ListItem, ListView, Static
from bilibili_api import Credential, Danmaku, live_area, live
from bilibili_api.live import LiveRoom, LiveDanmaku

from utils.room_utils import load_room_ids

ROOM_IDS = load_room_ids(csv_path="roomlist.csv")

load_dotenv()
SESSDATA = os.getenv("SESSDATA")
BILI_JCT = os.getenv("BILI_JCT")
credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT)


class RoomList(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield ListView(
            *[
                ListItem(
                    Label(str(room_id)),
                    id=f"room-{room_id}",
                )
                for room_id in ROOM_IDS
            ],
            id="room_list",
        )


class RoomInfo(VerticalGroup):
    room_info = reactive({})

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="room_meta"):
                yield Label("Room ID: ", id="room_id")
                yield Label("Online Num: ", id="online_num")
            yield ListView(
                *[
                    ListItem(Label(str(rank)), id=f"rank-{rank}")
                    for rank in range(1, 11)
                ],
                id="online_rank",
            )

    def on_mount(self) -> None:
        self.room_id_label = self.query_one("#room_id", Label)
        self.online_num_label = self.query_one("#online_num", Label)
        self.online_rank_list = self.query_one("#online_rank", ListView)

    def watch_room_info(self, room_info: dict) -> None:
        room_id = room_info.get("room_id", "")
        online_num = room_info.get("online_num", "")
        online_rank = room_info.get("online_rank", [])
        self.room_id_label.update(f"Room ID: {room_id}")
        self.online_num_label.update(f"Online Num: {online_num}")

        # Replace list items in a way that triggers a refresh.
        self.online_rank_list.clear()
        self.online_rank_list.extend(
            [
                ListItem(Label(f"{rank['userRank']} {rank['uid']} {rank['name']}"))
                for rank in online_rank
            ]
        )

    async def update_room_info(self, info: dict) -> None:
        room_id = info["room_id"]
        room = LiveRoom(room_id, credential=credential)

        info = await room.get_gaonengbang()
        online_num = info["onlineNum"]
        online_rank = info["OnlineRankItem"]

        self.room_info = {
            "room_id": room_id,
            "online_num": online_num,
            "online_rank": online_rank,
        }


class BiliBotApp(App):
    """A Textual app to play audio."""

    CSS_PATH = "ui.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Horizontal(id="main"):
            yield RoomList(id="sidebar")
            yield RoomInfo(id="room_info")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "room_list":
            return
        item = event.item
        if item is None:
            return
        room_id = (item.id or "").removeprefix("room-")
        await self.query_one("#room_info", RoomInfo).update_room_info(
            {"room_id": room_id}
        )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
