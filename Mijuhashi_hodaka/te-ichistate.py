#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy

from yasmin import State
from yasmin import Blackboard

from rclpy.node import Node
from action_msgs.msg import GoalStatus

from navigation_sample1 import NavigationSample


class TeiichiState(State):
    def __init__(self, node: Node):

        # このステートが返せる結果
        super().__init__(outcomes=["success", "failure"])

        self.node = node

        # Navigationクラス生成
        self.nav = NavigationSample()

    def execute(self, blackboard: Blackboard) -> str:

        self.node.get_logger().info("Executing TEIICHI state")

        # 目的地設定

        goal_x = 1.0
        goal_y = 0.0
        goal_yaw = 0.0

        # ナビゲーション開始

        accepted = self.nav.goToPose(x=goal_x, y=goal_y, yaw=goal_yaw)

        # Goal拒否
        if not accepted:
            self.node.get_logger().error("Goal rejected")
            return "failure"

        # ナビゲーション完了待ち

        while not self.nav.isNavComplete():
            feedback = self.nav.getFeedback()

            if feedback is not None:
                self.node.get_logger().info(
                    f"Distance remaining: {feedback.distance_remaining}"
                )

        # 結果判定

        result = self.nav.getResult()

        if result == GoalStatus.STATUS_SUCCEEDED:
            self.node.get_logger().info("Navigation succeeded")

            return "success"

        else:
            self.node.get_logger().error("Navigation failed")

            return "failure"
