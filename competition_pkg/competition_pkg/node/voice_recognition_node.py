import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SpeechTextPublisher(Node):
    def __init__(self):
        super().__init__("speech_text_publisher")

        self.publisher = self.create_publisher(
            String,
            "speech_text",
            10
        )

    def publish_recognized_text(self, recognized_text: str):
        msg = String()
        msg.data = recognized_text
        self.publisher.publish(msg)

        self.get_logger().info(f"送信した音声認識結果: {recognized_text}")


def main(args=None):
    rclpy.init(args=args)

    node = SpeechTextPublisher()

    # 動作確認用：本来はここに音声認識結果を入れる
    node.publish_recognized_text("HAVE")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()