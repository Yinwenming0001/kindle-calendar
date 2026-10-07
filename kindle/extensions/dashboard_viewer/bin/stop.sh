#!/bin/sh
# 停止台历，恢复自动屏保
# 注意：本文件必须保持 Unix 换行符（LF）

EXT_DIR="/mnt/us/extensions/dashboard_viewer"
PIDFILE="$EXT_DIR/bin/dashboard_viewer.pid"
LOG="$EXT_DIR/dashboard_viewer.log"

if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
    rm -f "$PIDFILE"
fi

pkill -f dashboard_viewer.sh 2>/dev/null
lipc-set-prop com.lab126.powerd preventScreenSaver 0 2>/dev/null

eips 20 40 "台历已停止"
echo "$(date '+%F %T') 台历已停止" >> "$LOG"
