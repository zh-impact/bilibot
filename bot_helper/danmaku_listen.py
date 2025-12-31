from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku, LiveRoom


def danmaku_listen(roomid: int, credential: Credential):
    danmaku = LiveDanmaku(roomid, credential=credential)

    DANMAKU_TYPES = {
        "SEND_GIFT": "SEND_GIFT",
        "DANMU_MSG": "DANMU_MSG",
        "INTERACT_WORD_V2": "INTERACT_WORD_V2",
        "COMBO_SEND": "COMBO_SEND",
        "GUARD_BUY": "GUARD_BUY",
        "SUPER_CHAT_MESSAGE": "SUPER_CHAT_MESSAGE",
        "WELCOME_GUARD": "WELCOME_GUARD",
        "DISCONNECT": "DISCONNECT",
    }

    @danmaku.on(DANMAKU_TYPES["DANMU_MSG"])
    async def on_danmu_msg(event):
        print("-" * 30, "DANMU_MSG", "-" * 30)
        info = event["data"]["info"]
        msg = info[1]
        print(f"{info[2][1]}: {msg}")
        print("-" * 30)

    @danmaku.on(DANMAKU_TYPES["SEND_GIFT"])
    async def on_send_gift(event):
        print("-" * 30, "SEND_GIFT", "-" * 30)
        data = event["data"]["data"]
        print(f"{data['uname']} {data['action']} {data['num']} {data['giftName']}")
        print("-" * 30)

    @danmaku.on(DANMAKU_TYPES["INTERACT_WORD_V2"])
    async def on_interact_word_v2(event):
        print("-" * 30, "INTERACT_WORD_V2", "-" * 30)
        decode_message = event["data"]["data"]["pb_decode_message"]
        if decode_message == "success":
            user_name = event["data"]["data"]["pb_decoded"]["uname"]
            print(f"{user_name} 进入直播间")
        else:
            print("Decode failed")
        print("-" * 30)
