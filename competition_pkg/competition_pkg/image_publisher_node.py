import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')

        image_path = os.path.expanduser(
            '~/ros2_lecture_ws/src/7_lectures/competition_pkg/image/test_image.jpg'
        )

        self.img = cv2.imread(image_path)
        if self.img is None:
            self.get_logger().error(f'画像が読み込めません: {image_path}')
            return

        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.timer = self.create_timer(1.0, self.publish_image)
        self.get_logger().info('ImagePublisher 起動しました')

    def publish_image(self):
        msg = self.bridge.cv2_to_imgmsg(self.img, 'bgr8')
        self.pub.publish(msg)
        self.get_logger().info('画像を配信しました')


def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()