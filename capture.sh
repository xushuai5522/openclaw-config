#!/bin/bash
# 持续截屏脚本 - 每0.5秒截一次
# 用法: ./capture.sh [秒数]
# 默认截60秒

DURATION=${1:-60}
INTERVAL=0.5
OUTPUT_DIR="/tmp/rrz_capture"
mkdir -p $OUTPUT_DIR

echo "开始录屏，持续${DURATION}秒..."
echo "按 Ctrl+C 停止"

count=0
while [ $count -lt $(($DURATION * 2)) ]; do
    screencapture -x "$OUTPUT_DIR/frame_$(printf '%04d' $count).png"
    count=$((count + 1))
    sleep $INTERVAL
done

echo "录制完成！共 $(ls $OUTPUT_DIR | wc -l) 张截图"
echo "保存在: $OUTPUT_DIR"
