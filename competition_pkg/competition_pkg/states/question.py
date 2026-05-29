import rclpy
from rclpy.node import Node

from yasmin import State
from yasmin import Blackboard


class QuestionState(State):
    def __init__(self, node: Node):
        super().__init__(outcomes=["success"])

        self.node = node

    def execute(self, blackboard: Blackboard):
        self.node.get_logger().info("鍵持ってますか？")

        return "success"