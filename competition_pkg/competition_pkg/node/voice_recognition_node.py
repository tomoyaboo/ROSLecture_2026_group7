# モジュールのインポート（ROS2関連）
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class SpeechRecognitionNode(Node):
    def __init__(self):
        super().__init__("speech_recognition_node")

        self.speech_pub = self.create_publisher(
            msg_type=String,
            topic="speech_text",
            qos_profile=10
        )

        self.get_logger().info("音声認識ノードを開始しました")
        self.get_logger().info("HAVE または LOST を入力してください")

    def run(self):
        while rclpy.ok():
            text = input("音声認識結果を入力: ")
            text = text.strip().upper()

            msg = String()
            msg.data = text

            self.speech_pub.publish(msg)
            self.get_logger().info(f"/speech_text に送信: {text}")


def main(args=None):
    rclpy.init(args=args)

    node = SpeechRecognitionNode()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()