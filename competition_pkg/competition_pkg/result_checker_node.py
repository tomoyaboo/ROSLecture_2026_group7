import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

class ResultChecker(Node):
    def __init__(self):
        super().__init__('result_checker')
        self.create_subscription(Bool, '/key_detected', self.callback, 10)
        self.get_logger().info('ResultChecker 起動しました')

    def callback(self, msg):
        if msg.data:
            self.get_logger().info('鍵を検出しました！')
        else:
            self.get_logger().info('鍵は検出されませんでした')


def main(args=None):
    rclpy.init(args=args)
    node = ResultChecker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()