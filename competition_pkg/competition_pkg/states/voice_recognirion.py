# モジュールのインポート(ROS2関連)
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node

# モジュールのインポート（YASMIN関連）
# https://github.com/uleroboticsgroup/yasmin.git
from yasmin import State
from yasmin import Blackboard

from std_msgs.msg import String

class VoRecofg(State):
    def __init__(self, node : Node):
        super().__init__(outcomes=["success", "failure", "retry"])

        self.node = node
        self.latest_speech_text = ""

        self.speech_sub = self.node.create_subscription(
            msg_type=String,
            topic="speech_text",
            callback=self.speech_callback,
            qos_profile=10
        )

        self.speech_pub = self.node.create_publisher(
            msg_type=String,
            topic="speech_command",
            qos_profile=10
        )

        self.expected_text_Y = "HAVE"
        self.expected_text_N = "LOST"



    def speech_callback(self, msg: String):
        self.latest_speech_text = msg.data
        self.node.get_logger().info(f"音声認識結果: {msg.data}")

    def publish_speech(self, text: str):
        msg = String()
        msg.data = text
        self.speech_pub.publish(msg)
        self.node.get_logger().info(f"音声出力命令: {text}")




    def execute(self, blackboard: Blackboard):
        self.node.get_logger().info("発話認識のステートを開始しています")


        start_time = self.node.get_clock().now()

        while rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.1)

            text = self.latest_speech_text

            if text == self.expected_text_Y:
                self.node.get_logger().info("HAVEと認識しました")
                return "success"

            elif text == self.expected_text_N:
                self.node.get_logger().info("LOSTと認識しました")
                return "failure"

            now = self.node.get_clock().now()
            if now - start_time > Duration(seconds=5):
                self.node.get_logger().info("5秒以内にHAVE/LOSTを認識できませんでした")
                return "retry"

