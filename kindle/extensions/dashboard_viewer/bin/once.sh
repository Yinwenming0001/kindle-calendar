#!/bin/sh
# 立即刷新一次画面
# 注意：本文件必须保持 Unix 换行符（LF）

EXT_DIR="/mnt/us/extensions/dashboard_viewer"
SETTINGS="$EXT_DIR/dashboard_viewer_settings.txt"
TMP="/tmp/dashboard.png"
LOG="$EXT_DIR/dashboard_viewer.log"

URL=$(grep -E "^url=" "$SETTINGS" 2>/dev/null | head -1 | cut -d= -f2-)

LOCAL="/mnt/us/calendar.png"

if [ -z "$URL" ]; then
    if [ -s "$LOCAL" ]; then
        eips -f -g "$LOCAL"
        echo "$(date '+%F %T') 离线模式，已显示本地 calendar.png" >> "$LOG"
    else
        echo "$(date '+%F %T') 未配置图片地址" >> "$LOG"
        eips 15 30 "请先配置 url，或把 calendar.png 拷到 Kindle 根目录"
    fi
    exit 1
fi

# GitHub Pages 有 CDN 缓存，带时间戳绕过
N="$(date +%s)"
case "$URL" in
    *\?*) FETCH_URL="$URL" ;;
    *)    FETCH_URL="$URL?t=$N" ;;
esac

rm -f "$TMP"
if command -v curl > /dev/null 2>&1; then
    curl -sL -m 90 -o "$TMP" "$FETCH_URL"
    SZ=$(wc -c < "$TMP" 2>/dev/null)
    if [ "${SZ:-0}" -lt 2000 ]; then
        curl -sL -k -m 90 -o "$TMP" "$URL"
    fi
elif command -v wget > /dev/null 2>&1; then
    wget -q -T 90 -O "$TMP" "$FETCH_URL"
fi

SZ=$(wc -c < "$TMP" 2>/dev/null)
echo "$(date '+%F %T') 下载字节数 ${SZ:-0}" >> "$LOG"

if [ -s "$TMP" ] && [ "${SZ:-0}" -gt 2000 ]; then
    eips -f -g "$TMP"
    echo "$(date '+%F %T') 手动刷新成功" >> "$LOG"
elif [ -s "$LOCAL" ]; then
    eips -f -g "$LOCAL"
    echo "$(date '+%F %T') 下载失败，改用本地 calendar.png" >> "$LOG"
else
    eips 20 40 "下载失败，请检查网络或地址"
    echo "$(date '+%F %T') 手动刷新失败" >> "$LOG"
fi
