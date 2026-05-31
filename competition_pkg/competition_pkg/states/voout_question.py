import pyttsx3

from yasmin import State
from yasmin import Blackboard


class QuestionState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])

        self.node = node


    def execute(self, blackboard: Blackboard):

        self.node.get_logger().info("Executing Question State")

        try:
         
            self.node.get_logger().info("鍵を持っていますか")

            return "success"

        except Exception as e:
            sself.node.get_logger().info("failure")

            return "failure"
