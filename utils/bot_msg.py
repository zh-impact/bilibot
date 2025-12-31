import random
import time


def check_time_range():
    range = ["早上好", "下午好", "晚上好"]
    now = time.localtime()
    hour = now.tm_hour

    if 5 <= hour < 12:
        return range[0]
    elif 12 <= hour < 18:
        return range[1]
    else:
        return range[2]


GENERAL_MSGS = [
    "万水千山总是情，点个关注行不行～",
    "进来了就点点关注哦，主播很可爱哒～",
    "喜欢的话，就留下来，嗷呜嗷呜～",
    "多多互动喔，{} 喜欢交朋友～",
]

WELCOME_USER_MSGS = [
    "欢迎 {}，捕捉一只小可爱～",
    "欢迎 {}，你终于来啦～",
    "欢迎 {} 光临～",
    # "欢迎 {} 早安|午安|晚安|～",
    "欢迎 {}，来和我们一起玩耍吧～",
    "欢迎 {} 宝子嗷呜～",
]

WELCOME_CAPTAIN_MSGS = [
    "欢迎舰长大人 {} 回家～",
]

WELCOME_ADMIRAL_MSGS = [
    "欢迎提督大人 {} 回家～",
]

WELCOME_GOVERNOR_MSGS = [
    "欢迎总督大人 {} 回家～",
]

RELATIONS = []


def get_welcome_msg(name: str, level: int):
    MSG = WELCOME_USER_MSGS
    if level == 3:
        MSG = WELCOME_CAPTAIN_MSGS
    elif level == 4:
        MSG = WELCOME_ADMIRAL_MSGS
    elif level == 5:
        MSG = WELCOME_GOVERNOR_MSGS
    return random.choice(MSG).format(name)
