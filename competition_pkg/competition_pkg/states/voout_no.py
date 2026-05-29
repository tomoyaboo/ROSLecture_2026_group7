import pyttsx3

from yasmin import State
from yasmin import Blackboard


class VoOutNoState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])

        self.node = node
        self.engine = pyttsx3.init()

    def execute(self, blackboard: Blackboard):

        self.node.get_logger().info("Executing VoOut-No State")

        try:
            self.engine.say("鍵がないです")
            self.engine.runAndWait()

            return "success"

        except Exception as e:
            self.node.get_logger().error(
                f"Voice output failed: {e}"
            )

            return "failure"