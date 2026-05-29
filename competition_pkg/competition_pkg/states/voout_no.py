#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from yasmin import State
from yasmin import Blackboard


class VoOutNoState(State):
    def __init__(self, node):
        super().__init__(outcomes=["success", "failure"])
        self.node = node

    def execute(self, blackboard: Blackboard) -> str:
        self.node.get_logger().info("Executing VoOut-No state")

        try:
            subprocess.run(["spd-say", "鍵がないです"], check=True)
            return "success"
        except Exception as e:
            self.node.get_logger().error(f"Voice output failed: {e}")
            return "failure"