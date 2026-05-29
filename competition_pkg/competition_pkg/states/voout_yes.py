import os
import subprocess

from yasmin import State
from yasmin import Blackboard


class VoOutYesState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])
        self.node = node

    def execute(self, blackboard: Blackboard):
        try:
            voice_path = os.path.expanduser(
                "~/ROSLecture_2026_group7/competition_pkg/competition_pkg/states/voout_yes.mp3"
            )

            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", voice_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return "success"

        except Exception as e:
            self.node.get_logger().error(f"Voice playback failed: {e}")
            return "failure"