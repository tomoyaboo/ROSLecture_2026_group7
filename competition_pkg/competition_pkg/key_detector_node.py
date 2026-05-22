import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String
from cv_bridge import CvBridge
import torch
import cv2
import numpy as np
import os

class KeyDetectorNode(Node):
    def __init__(self):
        super().__init__('key_detector')

        # weightsのパス
        weights_path = os.path.expanduser(
            '~/ros2_lecture_ws/src/7_lectures/competition_pkg/yolo/yolov5s.pt'
        )

        # YOLOv5ロード
        self.model = torch.hub.load('ultralytics/yolov5', 'custom',
                                     path=weights_path)
        self.model.conf = 0.35
        self.model.imgsz = 640

        self.bridge = CvBridge()
        self.current_state = ''  # 現在のステート

        # Subscribe
        self.create_subscription(
            String,
            '/current_state',
            self.state_callback,
            10
        )
        self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publish
        self.pub = self.create_publisher(Bool, '/key_detected', 10)

        self.get_logger().info('KeyDetectorNode 起動しました')

    def state_callback(self, msg):
        self.current_state = msg.data
        self.get_logger().info(f'ステート更新: {self.current_state}')

    def image_callback(self, msg):
        # ob-recogステートのときだけ検出する
        if self.current_state != 'ob-recog':
            return

        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        results = self.model(frame)
        detections = results.pandas().xyxy[0]

        detected = False
        if len(detections) > 0:
            detected = self.check_pink(frame, detections)

        self.pub.publish(Bool(data=detected))
        self.get_logger().info(f'検出結果: {detected}')

    def check_pink(self, frame, detections):
        for _, row in detections.iterrows():
            x1, y1, x2, y2 = int(row.xmin), int(row.ymin), \
                              int(row.xmax), int(row.ymax)
            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower = np.array([140, 50, 100])
            upper = np.array([170, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            pink_ratio = mask.sum() / (roi.shape[0] * roi.shape[1] + 1e-5)
            if pink_ratio > 0.01:
                return True
        return False


def main(args=None):
    rclpy.init(args=args)
    node = KeyDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()