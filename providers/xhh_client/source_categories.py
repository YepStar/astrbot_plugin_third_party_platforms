"""Fallback category aliases from Xiaoheihe adapter (MIT); topic-first policy."""
SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "all": (),
    "pc_game": ("pc游戏", "pc 游戏", "steam游戏", "steam", "单机游戏"),
    "mobile_game": ("手机游戏", "手游"),
    "console_game": ("主机游戏", "switch", "xbox", "playstation", "ps5", "ps4", "任天堂"),
    "community": ("盒友杂谈", "杂谈"),
    "daily": ("盒友日常", "日常", "生活"),
    "digital_tech": ("数码科技", "数码", "硬件", "外设", "科技"),
    "anime": ("动漫", "二次元", "漫画", "番剧", "同人"),
    "film_tv": ("影视", "电影", "电视剧", "综艺"),
    "esports": ("电竞", "赛事"),
    "guide": ("攻略", "心得", "教程"),
    "deals": ("特惠资讯", "优惠", "折扣", "史低"),
    "indie_game": ("独立游戏", "indie"),
}


def matches(post,sources):
    if "all" in sources:return True
    aliases=[a.casefold() for s in sources for a in SECTION_ALIASES.get(s,())]
    return any(alias in str(name).casefold() for name in post.get("section_names",[]) for alias in aliases)
