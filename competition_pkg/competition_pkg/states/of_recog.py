#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import cv2
import torch
import numpy as np

from yasmin import State
from yasmin import Blackboard


class ObRecogState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])
        self.node = node

        # YOLOv5モデルのロード
        weights_path = os.path.expanduser(
            '/ros2/ros2_lecture_ws/install/competition_pkg/lib/python3.10/site-packages/competition_pkg/yolo/best.pt'
        )
        yolov5_path = os.path.expanduser(
            '/home/ros2/ros2_lecture_ws/install/competition_pkg/lib/python3.10/site-packages/ROSLecture_2026_group7/competition_pkg/yolov5'
        )
        self.model = torch.hub.load(
            yolov5_path, 'custom',
            path=weights_path,
            source='local'
        )
        self.model.conf = 0.7   # 信頼度閾値
        self.model.imgsz = 640
        self.node.get_logger().info("YOLOv5モデルのロード完了")

    def execute(self, blackboard: Blackboard) -> str:
        self.node.get_logger().info("ob-recog ステート開始")

        # カメラ起動
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.node.get_logger().error("カメラを開けませんでした")
            return "failure"

        detect_start_time = None   # 検出開始時刻
        REQUIRED_SEC = 3.0         # 継続検出が必要な秒数
        TIMEOUT_SEC  = 30.0        # タイムアウト（30秒で諦める）
        start_time   = time.time()

        try:
            while True:
                # タイムアウト判定
                elapsed = time.time() - start_time
                if elapsed > TIMEOUT_SEC:
                    self.node.get_logger().warn("タイムアウト: keyを検出できませんでした")
                    return "failure"

                ret, frame = cap.read()
                if not ret:
                    self.node.get_logger().warn("フレームを取得できませんでした")
                    continue

                # YOLOv5推論
                results = self.model(frame)
                detections = results.pandas().xyxy[0]

                # keyかつconf>=0.8の検出があるか
                key_detected = any(
                    row['name'] == 'key' and row['confidence'] >= 0.8
                    for _, row in detections.iterrows()
                )

                if key_detected:
                    if detect_start_time is None:
                        detect_start_time = time.time()
                        self.node.get_logger().info("key検出開始、継続確認中...")

                    # 3秒以上継続して検出できたか
                    duration = time.time() - detect_start_time
                    self.node.get_logger().info(f"継続検出時間: {duration:.1f}秒")

                    if duration >= REQUIRED_SEC:
                        self.node.get_logger().info("✅ keyを3秒以上検出！success")
                        return "success"
                else:
                    # 検出が途切れたらリセット
                    if detect_start_time is not None:
                        self.node.get_logger().info("検出が途切れました。リセット")
                    detect_start_time = None

        finally:
            cap.release()
