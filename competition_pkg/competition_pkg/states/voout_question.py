import subprocess
from gtts import gTTS

from yasmin import State
from yasmin import Blackboard


class QuestionState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])
        self.node = node

    def execute(self, blackboard: Blackboard):

        self.node.get_logger().info("Executing Question State")

        try:
            tts = gTTS("鍵を持っていますか", lang="ja")
            tts.save("/tmp/question.mp3")

            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "/tmp/question.mp3"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return "success"

        except Exception as e:
            self.node.get_logger().error(
                f"Voice output failed: {e}"
            )
            return "failure"