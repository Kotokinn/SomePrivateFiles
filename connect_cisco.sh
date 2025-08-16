#!/bin/bash
PORTS=($(ls /dev/ttyUSB* /dev/ttyS* 2>/dev/null))
if [ ${#PORTS[@]} -eq 0 ]; then
    echo "Không tìm thấy cổng COM nào."
    exit 1
fi

echo "Các cổng COM khả dụng:"
for i in "${!PORTS[@]}"; do
    echo "$((i+1)). ${PORTS[$i]}"
done

read -p "Chọn số: " CHOICE
PORT=${PORTS[$((CHOICE-1))]}

echo "Chọn baudrate:"
options=(9600 19200 38400 57600 115200)
for i in "${!options[@]}"; do
    echo "$((i+1)). ${options[$i]}"
done

read -p "Chọn số baudrate: " BCHOICE
BAUD=${options[$((BCHOICE-1))]}

echo "Kết nối $PORT ở $BAUD..."
screen "$PORT" "$BAUD"
