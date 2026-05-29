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

        # 縺薙�ｮ繧ｹ繝�繝ｼ繝医′霑斐○繧狗ｵ先棡
        super().__init__(outcomes=["success", "failure"])

        self.node = node

        # Navigation繧ｯ繝ｩ繧ｹ逕滓��
        self.nav = NavigationSample()

    def execute(self, blackboard: Blackboard) -> str:

        self.node.get_logger().info("Executing TEIICHI state")

        # 逶ｮ逧�蝨ｰ險ｭ螳�

        goal_x = 1.0
        goal_y = 0.0
        goal_yaw = 0.0

        # 繝翫ン繧ｲ繝ｼ繧ｷ繝ｧ繝ｳ髢句ｧ�

        accepted = self.nav.goToPose(x=goal_x, y=goal_y, yaw=goal_yaw)

        # Goal諡貞凄
        if not accepted:
            self.node.get_logger().error("Goal rejected")
            return "failure"

        # 繝翫ン繧ｲ繝ｼ繧ｷ繝ｧ繝ｳ螳御ｺ�蠕�縺｡

        while not self.nav.isNavComplete():
            feedback = self.nav.getFeedback()

            if feedback is not None:
                self.node.get_logger().info(
                    f"Distance remaining: {feedback.distance_remaining}"
                )

        # 邨先棡蛻､螳�

        result = self.nav.getResult()

        if result == GoalStatus.STATUS_SUCCEEDED:
            self.node.get_logger().info("Navigation succeeded")

            return "success"

        else:
            self.node.get_logger().error("Navigation failed")

            return "failure"
