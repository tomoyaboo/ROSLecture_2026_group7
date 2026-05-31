import pyttsx3

from yasmin import State
from yasmin import Blackboard


class VoOutHaveState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])

        self.node = node


    def execute(self, blackboard: Blackboard):

        self.node.get_logger().info("Executing VoOut-Have State")

        try:
            self.node.get_logger().info("鍵を持っているんですね")
            return "success"

        except Exception as e:
            self.node.get_logger().info("failure")
            return "failure"
