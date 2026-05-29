import subprocess

from yasmin import State
from yasmin import Blackboard


class QuestionState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])

        self.node = node

    def execute(self, blackboard: Blackboard):

        self.node.get_logger().info("Executing Question State")

        try:
            # 音声出力
            subprocess.run(
                ["spd-say", "鍵を持ってますか"],
                check=True
            )

            # 音声認識ステートへ
            return "success"

        except Exception as e:
            self.node.get_logger().error(
                f"Voice output failed: {e}"
            )

            return "failure"