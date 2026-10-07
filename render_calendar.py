#!/usr/bin/env python3
"""Kindle 台历图片生成器

生成一张适配 Kindle 屏幕的 8 位灰度 PNG：
日期 + 农历节气 + 天气 + 节日倒计时 + 每日一句

用法:
    python3 render_calendar.py --city 北京 --lat 39.9042 --lon 116.4074 \
        --width 1072 --height 1448 --out preview.png
"""

import argparse
import datetime
import math
import os
import sys
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor", "lunar_python-1.4.8"))
from lunar_python import Solar  # noqa: E402

# 常见机型分辨率
DEVICES = {
    "basic11": (1072, 1448),   # Kindle 入门版 11/12 代 (2022/2024, 300ppi)
    "basic10": (600, 800),     # Kindle 入门版 10 代及更早 (167ppi)
    "pw5": (1236, 1648),       # Paperwhite 5
    "pw6": (1272, 1696),       # Paperwhite 6
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf",
]

WMO = {
    0: "晴", 1: "晴间多云", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇", 51: "小雨", 53: "中雨", 55: "大雨",
    56: "冻雨", 57: "冻雨", 61: "小雨", 63: "中雨", 65: "大雨",
    66: "冻雨", 67: "冻雨", 71: "小雪", 73: "中雪", 75: "大雪",
    77: "米雪", 80: "阵雨", 81: "阵雨", 82: "暴雨",
    85: "阵雪", 86: "阵雪", 95: "雷阵雨", 96: "雷阵雨伴冰雹", 99: "强雷暴",
}

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

QUOTES = [
    "一日之计在于晨，一年之计在于春。",
    "不积跬步，无以至千里。",
    "生活不是等待暴风雨过去，而是学会在雨中起舞。",
    "慢一点也没关系，只要方向是对的。",
    "把今天过好，就是对未来最好的准备。",
    "所有的努力都不会白费，它们只是在等一个时机。",
    "愿你今天遇到的每一件小事，都值得被记住。",
    "所谓自由，不是随心所欲，而是自我主宰。",
    "家人闲坐，灯火可亲。",
    "读书是最低门槛的高贵。",
    "与其焦虑明天，不如认真吃饭、好好睡觉。",
    "时间从不会辜负一个默默努力的人。",
    "世界很大，慢慢看。",
    "心若向阳，无畏悲伤。",
    "每一个不曾起舞的日子，都是对生命的辜负。",
    "真正的成熟，是知道怎样与不确定相处。",
    "把复杂的事做简单，是本事；把简单的事做到底，是本事。",
    "愿你所求皆如愿，所行化坦途。",
    "星光不问赶路人，时光不负有心人。",
    "今天也要好好生活呀。",
]


def load_font(size, bold=False):
    for path in FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def fetch_weather(lat, lon, timeout=20):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Shanghai",
        "forecast_days": 1,
    }
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        d = r.json()
        cur = d["current"]
        day = d["daily"]
        return {
            "temp": round(cur["temperature_2m"]),
            "code": cur["weather_code"],
            "desc": WMO.get(cur["weather_code"], "—"),
            "tmax": round(day["temperature_2m_max"][0]),
            "tmin": round(day["temperature_2m_min"][0]),
            "pop": day["precipitation_probability_max"][0],
            "wind": round(cur["wind_speed_10m"]),
        }
    except Exception as e:
        print(f"[warn] 天气获取失败: {e}", file=sys.stderr)
        return {"temp": None, "code": None, "desc": "—", "tmax": None,
                "tmin": None, "pop": None, "wind": None}


def next_festival(today, within=120):
    """返回 (名称, 剩余天数)，公历节日与农历节日都算"""
    for delta in range(1, within + 1):
        d = datetime.datetime.combine(today + datetime.timedelta(days=delta),
                                      datetime.time(12, 0))
        solar = Solar.fromDate(d)
        names = list(solar.getFestivals()) + list(solar.getLunar().getFestivals())
        names = [n for n in names if n and "纪念日" not in n]
        if names:
            return names[0], delta
    return None, None


def build_lunar_info(today):
    solar = Solar.fromDate(datetime.datetime.combine(today, datetime.time(12, 0)))
    lunar = solar.getLunar()
    jieqi = lunar.getJieQi()          # 当天节气（非节气日为空）
    festivals = list(solar.getFestivals()) + list(lunar.getFestivals())
    festivals = [f for f in festivals if f]
    return {
        "lunar_month": lunar.getMonthInChinese(),
        "lunar_day": lunar.getDayInChinese(),
        "ganzhi": f"{lunar.getYearInGanZhi()}年 {lunar.getMonthInGanZhi()}月 {lunar.getDayInGanZhi()}日",
        "jieqi": jieqi,
        "festivals": festivals,
    }


def draw(draw, xy, text, font, fill=0, anchor="la"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def icon_kind(code):
    """把 Open-Meteo 天气码映射成图标类型"""
    if code is None:
        return None
    if code in (0, 1):
        return "sun"
    if code == 2:
        return "sun_cloud"
    if code == 3:
        return "cloud"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunder"
    return "cloud"


def draw_icon(d, kind, x, y, s, c):
    """在 (x, y) 画一个 s×s 的实心风格天气图标"""

    def cloud(cx, cy, cw):
        ch = cw * 0.62
        d.ellipse([cx, cy + ch * 0.32, cx + cw * 0.52, cy + ch], fill=c)
        d.ellipse([cx + cw * 0.30, cy + ch * 0.02, cx + cw * 0.90, cy + ch * 0.78], fill=c)
        d.ellipse([cx + cw * 0.52, cy + ch * 0.38, cx + cw, cy + ch], fill=c)
        d.rectangle([cx + cw * 0.04, cy + ch * 0.60, cx + cw * 0.96, cy + ch], fill=c)

    def sun(cx, cy, r, rays=True):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        if rays:
            w = max(2, int(r * 0.22))
            for i in range(8):
                a = i * math.pi / 4
                d.line([cx + math.cos(a) * r * 1.35, cy + math.sin(a) * r * 1.35,
                        cx + math.cos(a) * r * 1.8, cy + math.sin(a) * r * 1.8],
                       fill=c, width=w)

    def drops(cx, cy, w, n=3):
        lw = max(2, int(w * 0.075))
        for i in range(n):
            dx = cx + (i - (n - 1) / 2) * (w / n) * 0.9
            d.line([dx, cy, dx - w * 0.06, cy + w * 0.22], fill=c, width=lw)

    def flakes(cx, cy, w, n=3):
        r = max(2, w * 0.05)
        for i in range(n):
            dx = cx + (i - (n - 1) / 2) * (w / n) * 0.9
            d.ellipse([dx - r, cy, dx + r, cy + r * 2], fill=c)

    if kind == "sun":
        sun(x + s / 2, y + s / 2, s * 0.21)
    elif kind == "cloud":
        cloud(x + s * 0.05, y + s * 0.30, s * 0.90)
    elif kind == "sun_cloud":
        sun(x + s * 0.66, y + s * 0.28, s * 0.15)
        cloud(x + s * 0.02, y + s * 0.40, s * 0.82)
    elif kind == "fog":
        w = max(2, int(s * 0.055))
        for i in range(4):
            yy = y + s * 0.34 + i * s * 0.13
            x0 = x + s * 0.08 + (i % 2) * s * 0.08
            d.line([x0, yy, x0 + s * (0.84 - (i % 2) * 0.16), yy], fill=c, width=w)
    elif kind == "rain":
        cloud(x + s * 0.05, y + s * 0.16, s * 0.90)
        drops(x + s * 0.5, y + s * 0.70, s * 0.78)
    elif kind == "snow":
        cloud(x + s * 0.05, y + s * 0.16, s * 0.90)
        flakes(x + s * 0.5, y + s * 0.72, s * 0.78)
    elif kind == "thunder":
        cloud(x + s * 0.05, y + s * 0.10, s * 0.90)
        px, py = x + s * 0.44, y + s * 0.56
        d.polygon([(px + s * 0.06, py), (px - s * 0.14, py + s * 0.28),
                   (px + s * 0.02, py + s * 0.26), (px - s * 0.06, py + s * 0.40),
                   (px + s * 0.20, py + s * 0.10), (px + s * 0.02, py + s * 0.10)],
                  fill=c)


def render(city, lat, lon, w, h, out, photo=None, quote=None, datefactor=1.0):
    scale = w / 1072.0
    S = lambda v: int(round(v * scale))          # noqa: E731  布局尺寸
    FS = lambda v: int(round(v * max(scale, 0.68)))  # noqa: E731  字号（低分屏不过度缩小）

    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    M = S(80)          # 左右边距
    BLACK, GRAY, LIGHT = 0, 110, 190

    today = datetime.date.today()
    now = datetime.datetime.now()
    weather = fetch_weather(lat, lon)
    lunar = build_lunar_info(today)
    fest_name, fest_days = next_festival(today)

    f_city = load_font(FS(46))
    f_desc = load_font(FS(34))
    f_temp = load_font(FS(96))
    f_date = load_font(max(40, int(FS(200) * datefactor)))
    f_month = load_font(FS(38))
    f_lunar = load_font(FS(42))
    f_nianli = load_font(FS(34))   # 「2026年 农历八月二十七」单独用小一档
    f_body = load_font(FS(32))
    f_quote = load_font(FS(38))
    f_foot = load_font(FS(26))

    def text_h(font, s="中文字Ay1"):
        b = d.textbbox((0, 0), s, font=font)
        return b[3] - b[1]

    # ── 文案准备 ─────────────────────────────────────
    if quote is None:
        quote = QUOTES[today.timetuple().tm_yday % len(QUOTES)]
    max_chars = max(8, int((w - 2 * M) / (FS(38) * 0.98)))
    quote_lines = textwrap.wrap(quote, width=max_chars)[:3]

    badges = []
    if lunar["jieqi"]:
        badges.append("节气 · " + lunar["jieqi"])
    badges.extend(lunar["festivals"][:2])
    if not badges:
        badges.append(lunar["ganzhi"])

    if weather["tmax"] is not None:
        wline = f"最高 {weather['tmax']}°   最低 {weather['tmin']}°"
        if weather["pop"] is not None:
            wline += f"   降水 {weather['pop']}%"
        if weather["wind"] is not None and w >= 900:
            wline += f"   风 {weather['wind']} km/h"
    else:
        wline = "天气数据暂不可用"
    cd_text = f"距 {fest_name} 还有 {fest_days} 天" if fest_name else lunar["ganzhi"]
    lunar_text = f"{today.year}年  农历{lunar['lunar_month']}月{lunar['lunar_day']}"

    # ── 先测量每块高度，再把剩余空间均分成间距 ──────────
    h_city, h_desc = text_h(f_city), text_h(f_desc)
    h_month = text_h(f_month)
    h_date = text_h(f_date, f"{today.day:02d}")
    h_lunar = text_h(f_lunar, lunar_text)
    h_nianli = text_h(f_nianli, lunar_text)
    h_body = text_h(f_body, wline)
    h_quote = text_h(f_quote)
    h_foot = text_h(f_foot)
    badge_h = h_body + S(20)
    block_top = h_city + h_desc + S(4)
    block_quote = h_quote * len(quote_lines) + S(8) * max(0, len(quote_lines) - 1)

    blocks = [block_top, S(2), h_date, h_nianli, badge_h, h_body,
              h_lunar, S(2), block_quote, h_foot]
    gap = (h - 2 * M - sum(blocks)) / (len(blocks) - 1)
    gap = max(FS(16), min(gap, S(80)))
    # 间距封顶后仍有富余时，上下均分，让整屏内容垂直居中
    used = sum(blocks) + gap * (len(blocks) - 1)
    extra = max(0, (h - 2 * M) - used)

    y = M + extra / 2

    # ── 顶部：城市 / 天气描述 + 温度 ────────────────────
    draw(d, (M, y), city, f_city, BLACK)
    draw(d, (M, y + h_city + S(4)), weather["desc"], f_desc, GRAY)
    if weather["temp"] is not None:
        draw(d, (w - M, M), f"{weather['temp']}°", f_temp, BLACK, anchor="ra")
    y += block_top + gap

    d.line([(M, y), (w - M, y)], fill=LIGHT, width=max(1, S(2)))
    y += S(2) + gap

    # ── 日期 + 月份星期 ──────────────────────────────
    date_str = f"{today.day:02d}"
    draw(d, (M, y), date_str, f_date, BLACK)
    date_w = d.textlength(date_str, font=f_date)
    mx = M + date_w + S(24)
    draw(d, (mx, y + h_date * 0.34), f"{today.month}月", f_month, BLACK)
    draw(d, (mx, y + h_date * 0.34 + h_month + S(6)),
         WEEKDAYS[today.weekday()], f_month, GRAY)

    # 日期右侧留白处：放天气图标
    kind = icon_kind(weather.get("code"))
    if kind:
        isize = int(h_date * 0.82)
        ix = w - M - isize
        if ix > mx + S(96):
            draw_icon(d, kind, ix, y + (h_date - isize) / 2, isize, GRAY)
    y += h_date + gap

    # ── 公历年份 + 农历（小一档，贴近日期块） ─────────────
    draw(d, (M, y), lunar_text, f_nianli, BLACK)
    y += h_nianli + gap

    # ── 节气 / 节日徽章 ────────────────────────────────
    x = M
    for text in badges:
        tw = d.textlength(text, font=f_body)
        pad = S(16)
        bw = int(tw + pad * 2)
        if x + bw > w - M:
            break
        d.rounded_rectangle([x, y, x + bw, y + badge_h], radius=S(8),
                            outline=GRAY, width=max(1, S(2)))
        draw(d, (x + pad, y + badge_h / 2), text, f_body, GRAY, anchor="lm")
        x += bw + S(14)
    y += badge_h + gap

    # ── 天气明细 ─────────────────────────────────────
    draw(d, (M, y), wline, f_body, GRAY)
    y += h_body + gap

    # ── 节日倒计时 ────────────────────────────────────
    draw(d, (M, y), cd_text, f_lunar, BLACK)
    y += h_lunar + gap

    # ── 每日一句 ─────────────────────────────────────
    d.line([(M, y), (w - M, y)], fill=LIGHT, width=max(1, S(2)))
    y += S(2) + gap
    for i, line in enumerate(quote_lines):
        draw(d, (M, y + i * (h_quote + S(8))), line, f_quote, BLACK)
    y += block_quote + gap

    # ── 更新时间 ─────────────────────────────────────
    draw(d, (M, y), f"更新于 {now:%m-%d %H:%M}", f_foot, LIGHT)

    img.save(out, "PNG")
    print(f"已生成 {out}  {w}x{h} 灰度 PNG | 块间距 {gap:.0f}px，"
          f"内容底边 {y + h_foot:.0f} / 可用 {h - M}")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--city", default="常州 · 新北区")
    p.add_argument("--lat", type=float, default=31.86)
    p.add_argument("--lon", type=float, default=119.96)
    p.add_argument("--device", default="basic10", choices=list(DEVICES))
    p.add_argument("--width", type=int, default=None)
    p.add_argument("--height", type=int, default=None)
    p.add_argument("--photo", default=None, help="可选：底部插入一张家庭照片")
    p.add_argument("--quote", default=None)
    p.add_argument("--datefactor", type=float, default=1.0,
                   help="日期字号倍数：1.0 默认，嫌大填 0.8，想更醒目填 1.3")
    p.add_argument("--out", default="calendar.png")
    a = p.parse_args()

    w, h = (a.width, a.height) if a.width else DEVICES[a.device]
    render(a.city, a.lat, a.lon, w, h, a.out, a.photo, a.quote, a.datefactor)


if __name__ == "__main__":
    main()
