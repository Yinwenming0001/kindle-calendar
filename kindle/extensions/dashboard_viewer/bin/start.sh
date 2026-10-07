#!/bin/sh
# 启动台历：阻止屏保 + 后台常驻刷新
# 注意：本文件必须保持 Unix 换行符（LF）

EXT_DIR="/mnt/us/extensions/dashboard_viewer"
LOG="$EXT_DIR/dashboard_viewer.log"
PIDFILE="$EXT_DIR/bin/dashboard_viewer.pid"

lipc-set-prop com.lab126.powerd preventScreenSaver 1 2>/dev/null

if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
    rm -f "$PIDFILE"
fi

nohup /bin/sh "$EXT_DIR/bin/dashboard_viewer.sh" >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"

eips 20 40 "台历已启动，稍等几秒刷新"
echo "$(date '+%F %T') 台历已启动" >> "$LOG"
