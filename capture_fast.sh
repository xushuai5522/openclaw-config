#!/bin/bash
# 快速录屏脚本 - 每0.2秒截一次
# 用法: ./capture_fast.sh [秒数]

DURATION=${1:-60}
INTERVAL=0.2
OUTPUT_DIR="/tmp/rrz_capture"
mkdir -p $OUTPUT_DIR

# 清空旧文件
rm -f $OUTPUT_DIR/*.png

echo "开始录屏，每0.2秒截一张，持续${DURATION}秒..."
echo "按 Ctrl+C 停止"
echo "输出目录: $OUTPUT_DIR"

count=0
while [ $count -lt $(($DURATION * 5)) ]; do
    screencapture -x "$OUTPUT_DIR/frame_$(printf '%04d' $count).png"
    count=$((count + 1))
    sleep $INTERVAL
done

total=$(ls $OUTPUT_DIR/*.png 2>/dev/null | wc -l)
echo "录制完成！共 $total 张截图"
