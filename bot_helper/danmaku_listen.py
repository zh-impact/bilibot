import os
import time

from bilibili_api.live import LiveDanmaku

from utils.bot_msg import get_welcome_msg
from .ratelimit_sender import RateLimitSender

WAKE_WORD = "小坤小坤"


def run_command(msg: str):
    cmd = msg[len(WAKE_WORD) :]
    print(cmd)
    available_commands = ("你好", "天王盖地虎", "time")
    if cmd in available_commands:
        if cmd == "你好":
            return "你好"
        elif cmd == "天王盖地虎":
            return "宝塔镇河妖"
        elif cmd == "time":
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    else:
        # return run_ai_conversation(cmd)
        return None


def inspect_event(event, name: str):
    print("-" * 30, name or "Event", "-" * 30)
    print(event)
    print("-" * 30)


def danmaku_listen(danmaku: LiveDanmaku, send: callable, enabled_events=None):
    BOT_UID = os.getenv("BOT:UID")

    DANMAKU_TYPES = {
        "DANMU_MSG": "DANMU_MSG",  # 用户发送弹幕
        "SEND_GIFT": "SEND_GIFT",  # 礼物
        "COMBO_SEND": "COMBO_SEND",  # 礼物连击
        "GUARD_BUY": "GUARD_BUY",  # 续费大航海
        "SUPER_CHAT_MESSAGE": "SUPER_CHAT_MESSAGE",  # 醒目留言
        "WELCOME_GUARD": "WELCOME_GUARD",  # 房管进入房间
        "ROOM_REAL_TIME_MESSAGE_UPDATE": "ROOM_REAL_TIME_MESSAGE_UPDATE",  # 粉丝数等更新
        "INTERACT_WORD_V2": "INTERACT_WORD_V2",  # 用户进入直播间
        "DM_INTERACTION": "DM_INTERACTION",  # 交互信息合并
        "USER_TOAST_MSG": "USER_TOAST_MSG",  # 用户庆祝消息
        "GIFT_STAR_PROCESS": "GIFT_STAR_PROCESS",  # 礼物星球点亮
        "SPECIAL_GIFT": "SPECIAL_GIFT",  # 特殊礼物
        "LIKE_INFO_V3_CLICK": "LIKE_INFO_V3_CLICK",  # 直播间用户点赞
        "LIKE_INFO_V3_UPDATE": "LIKE_INFO_V3_UPDATE",  # 直播间点赞数更新
        "SYS_MSG": "SYS_MSG",  # 系统消息
        "WARNING": "WARNING",  # 警告消息
        "CUT_OFF": "CUT_OFF",  # 房间被切断
        "CUT_OFF_V2": "CUT_OFF_V2",  # 房间被切断v2
        "DISCONNECT": "DISCONNECT",
    }

    danmaku.enabled_events = set(
        enabled_events
        or [
            DANMAKU_TYPES["INTERACT_WORD_V2"],
            DANMAKU_TYPES["DANMU_MSG"],
            DANMAKU_TYPES["SEND_GIFT"],
            DANMAKU_TYPES["COMBO_SEND"],
            DANMAKU_TYPES["GUARD_BUY"],
            DANMAKU_TYPES["SUPER_CHAT_MESSAGE"],
        ]
    )

    def only_when(evt):
        def deco(fn):
            async def wrapped(event, *args, **kwargs):
                if evt not in danmaku.enabled_events:
                    return
                return await fn(event, *args, **kwargs)

            return wrapped

        return deco

    @danmaku.on(DANMAKU_TYPES["INTERACT_WORD_V2"])
    @only_when(DANMAKU_TYPES["INTERACT_WORD_V2"])
    async def on_interact_word_v2(event):
        inspect_event(event, "INTERACT_WORD_V2")
        decode_message = event["data"]["data"]["pb_decode_message"]
        if decode_message == "success":
            decoded = event["data"]["data"]["pb_decoded"]
            uname = decoded.get("uname", "神秘人")
            user_info = decoded.get("user_info", {})
            guard_info = user_info.get("guard", {})
            level = guard_info.get("level", 0)
            relation = decoded.get("user_anchor_relation", {})
            tail_guide_text = relation.get("tail_guide_text", "")

            print(f"{uname} 进入直播间")
            print(tail_guide_text)
            welcome_msg = get_welcome_msg(uname, level)
            await send(welcome_msg)
        else:
            print("Decode failed")

    @danmaku.on(DANMAKU_TYPES["DANMU_MSG"])
    @only_when(DANMAKU_TYPES["DANMU_MSG"])
    async def on_danmu_msg(event):
        inspect_event(event, "DANMU_MSG")
        info = event["data"]["info"]
        msg = info[1]
        print(f"{info[2][1]}: {msg}")
        print("-" * 30)

        uid = info[2][0]
        if uid == BOT_UID:
            return

        # print(msg.startswith(WAKE_WORD), uid, BOT_UID)
        if msg.startswith(WAKE_WORD):
            print(f"Bot command detected: {msg}")
            # TODO: Implement command processing
            # result = run_command(msg)
            # if result is not None:
            #     await ratelimit_sender.send(result)

    @danmaku.on(DANMAKU_TYPES["SEND_GIFT"])
    @only_when(DANMAKU_TYPES["SEND_GIFT"])
    async def on_send_gift(event):
        inspect_event(event, "SEND_GIFT")
        data = event["data"]["data"]
        uname = data["uname"]
        action = data["action"]
        num = data["num"]
        gift_name = data["giftName"]
        msg = f"感谢 {uname} {action}的{num}个{gift_name}"
        print(msg)

    @danmaku.on(DANMAKU_TYPES["COMBO_SEND"])
    @only_when(DANMAKU_TYPES["COMBO_SEND"])
    async def on_combo_send(event):
        inspect_event(event, "COMBO_SEND")
        data = event["data"]["data"]
        uname = data["uname"]
        action = data["action"]
        num = data["combo_num"]
        gift_name = data["gift_name"]
        msg = f"{uname} 共{action}了{num}个{gift_name}"
        print(msg)

    @danmaku.on(DANMAKU_TYPES["GUARD_BUY"])
    @only_when(DANMAKU_TYPES["GUARD_BUY"])
    async def on_guard_buy(event):
        inspect_event(event, "GUARD_BUY")
        data = event["data"]["data"]
        uname = data["username"]
        num = data["num"]
        gift_name = data["gift_name"]
        msg = f"感谢 {uname} 开通了 {num} 个 {gift_name}"
        print(msg)

    @danmaku.on(DANMAKU_TYPES["SUPER_CHAT_MESSAGE"])
    @only_when(DANMAKU_TYPES["SUPER_CHAT_MESSAGE"])
    async def on_super_chat(event):
        inspect_event(event, "SUPER_CHAT_MESSAGE")

    @danmaku.on(DANMAKU_TYPES["GIFT_STAR_PROCESS"])
    @only_when(DANMAKU_TYPES["GIFT_STAR_PROCESS"])
    async def on_gift_star_process(event):
        inspect_event(event, "GIFT_STAR_PROCESS")

    @danmaku.on(DANMAKU_TYPES["SPECIAL_GIFT"])
    @only_when(DANMAKU_TYPES["SPECIAL_GIFT"])
    async def on_special_gift(event):
        inspect_event(event, "SPECIAL_GIFT")

    @danmaku.on(DANMAKU_TYPES["LIKE_INFO_V3_CLICK"])
    @only_when(DANMAKU_TYPES["LIKE_INFO_V3_CLICK"])
    async def on_like_info_v3_click(event):
        inspect_event(event, "LIKE_INFO_V3_CLICK")
        data = event["data"]["data"]
        uname = data["uname"]
        print(f"{uname} 点赞了直播间")

    @danmaku.on(DANMAKU_TYPES["WARNING"])
    @only_when(DANMAKU_TYPES["WARNING"])
    async def on_warning(event):
        inspect_event(event, "WARNING")
