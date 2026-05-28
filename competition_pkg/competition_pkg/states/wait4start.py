import rclpy
from rclpy.node import Node

from yasmin import State
from yasmin import Blackboard


class Wait4startState(State):
    def __init__(self, node: Node):
        super().__init__(outcomes=["success"])

        self.node = node

    def execute(self, blackboard: Blackboard):
        self.node.get_logger().info("Wait4start: 開始待ちです")
        self.node.get_logger().info("開始するには y を入力してください")

        while rclpy.ok():
            user_input = input("Start? [y]: ")

            if user_input.strip().lower() == "y":
                self.node.get_logger().info("Wait4start: y が入力されたため開始します")
                return "success"

            self.node.get_logger().info("y を入力してください")