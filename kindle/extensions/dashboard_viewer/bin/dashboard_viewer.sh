#!/bin/sh
# 台历主循环：定时从 url 下载 PNG 并全屏显示
# 注意：本文件必须保持 Unix 换行符（LF）

EXT_DIR="/mnt/us/extensions/dashboard_viewer"
SETTINGS="$EXT_DIR/dashboard_viewer_settings.txt"
TMP="/tmp/dashboard.png"
LOG="$EXT_DIR/dashboard_viewer.log"

get_conf() {
    key="$1"
    default="$2"
    val=$(grep -E "^$key=" "$SETTINGS" 2>/dev/null | head -1 | cut -d= -f2-)
    if [ -z "$val" ]; then val="$default"; fi
    echo "$val"
}

URL=$(get_conf url "")
DAY_INT=$(get_conf dayinterval 1800)
NIGHT_INT=$(get_conf nightinterval 7200)
DAY_START=$(get_conf daystart 7)
DAY_END=$(get_conf dayend 23)

LOCAL="/mnt/us/calendar.png"

if [ -z "$URL" ] || [ "$URL" = "https://你的用户名.github.io/kindle-calendar/calendar.png" ]; then
    # 离线模式：显示根目录手动拷入的 calendar.png
    if [ -s "$LOCAL" ]; then
        eips -f -g "$LOCAL"
        echo "$(date '+%F %T') 离线模式，已显示本地 calendar.png" >> "$LOG"
    else
        echo "$(date '+%F %T') 未配置图片地址，也没有本地 calendar.png" >> "$LOG"
        eips 15 30 "请先配置 url，或把 calendar.png 拷到 Kindle 根目录"
    fi
    exit 1
fi

fetch() {
    # GitHub Pages 有 CDN 缓存，每次带新时间戳绕过，避免刷到旧图
    N="$(date +%s)"
    case "$URL" in
        *\?*) FETCH_URL="$URL" ;;
        *)    FETCH_URL="$URL?t=$N" ;;
    esac
    rm -f "$TMP"
    if command -v curl > /dev/null 2>&1; then
        curl -sL -m 90 -o "$TMP" "$FETCH_URL"
        # 老固件 TLS 握手可能失败，退一步重试一次
        SZ=$(wc -c < "$TMP" 2>/dev/null)
        if [ "${SZ:-0}" -lt 2000 ]; then
            curl -sL -k -m 90 -o "$TMP" "$URL"
        fi
    elif command -v wget > /dev/null 2>&1; then
        wget -q -T 90 -O "$TMP" "$FETCH_URL"
    fi
    SZ=$(wc -c < "$TMP" 2>/dev/null)
    if [ -s "$TMP" ] && [ "${SZ:-0}" -gt 2000 ]; then
        eips -f -g "$TMP"
        echo "$(date '+%F %T') 已刷新" >> "$LOG"
    elif [ -s "$LOCAL" ]; then
        eips -f -g "$LOCAL"
        echo "$(date '+%F %T') 下载失败，改用本地 calendar.png" >> "$LOG"
    else
        echo "$(date '+%F %T') 下载失败，保留上一画面" >> "$LOG"
    fi
}

echo "$(date '+%F %T') 台历循环启动：白天 ${DAY_INT}s / 夜间 ${NIGHT_INT}s" >> "$LOG"
fetch

while true; do
    H=$(date +%H | sed 's/^0*//')
    if [ -z "$H" ]; then H=0; fi
    if [ "$H" -ge "$DAY_START" ] && [ "$H" -lt "$DAY_END" ]; then
        sleep "$DAY_INT"
    else
        sleep "$NIGHT_INT"
    fi
    fetch
done
