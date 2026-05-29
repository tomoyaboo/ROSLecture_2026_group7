#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowWaypoints
from action_msgs.msg import GoalStatus

import tf_transformations

from yasmin import State
from yasmin import Blackboard

from .point_selector import AutoPointSelector


class SearchState(State):
    def __init__(self, node: Node, map_yaml_path: str):
        super().__init__(outcomes=["moved", "finished", "loop"])

        self.node = node
        self.map_yaml_path = map_yaml_path

        self.follow_waypoints_client = ActionClient(
            self.node,
            FollowWaypoints,
            "follow_waypoints"
        )

    def execute(self, blackboard: Blackboard) -> str:
        self.node.get_logger().info("Executing state SEARCH")

        # 初回実行時に探索ポイントを生成してBlackboardに保存
        if not hasattr(blackboard, "search_initialized"):
            self.node.get_logger().info("Initialize search waypoints")

            selector = AutoPointSelector(
                map_yaml_path=self.map_yaml_path,
                num_points=3,
                safety_distance_m=0.35,
                candidate_step_px=10,
                min_point_distance_m=0.8,
            )

            blackboard.search_waypoints = selector.select_points()
            blackboard.search_index = 0
            blackboard.search_initialized = True

            self.node.get_logger().info(
                f"Generated waypoints: {blackboard.search_waypoints}"
            )
        # すべての探索ポイントを回り終えたら終了
        if blackboard.search_index >= len(blackboard.search_waypoints):
            self.node.get_logger().info("All search points finished")
            return "finished"

        # 現在の探索ポイントに移動
        waypoint = blackboard.search_waypoints[blackboard.search_index]
        self.node.get_logger().info(
            f"Move to search point {blackboard.search_index + 1}: {waypoint}"
        )

        success = self._move_to_one_waypoint(waypoint)

        if not success:
            self.node.get_logger().error("Navigation failed")
            return "loop"

        blackboard.current_search_point = waypoint
        blackboard.search_index += 1

        return "moved"
    
    # 指定した1点に移動する。成功したらTrue、失敗したらFalseを返す。
    def _move_to_one_waypoint(self, waypoint) -> bool:
        while not self.follow_waypoints_client.wait_for_server(timeout_sec=1.0):
            self.node.get_logger().info(
                "'follow_waypoints' action server not available, waiting..."
            )

        pose = self._make_pose(waypoint)

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = [pose]

        send_goal_future = self.follow_waypoints_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self.node, send_goal_future)

        goal_handle = send_goal_future.result()

        if goal_handle is None or not goal_handle.accepted:
            self.node.get_logger().error("Goal rejected")
            return False

        result_future = goal_handle.get_result_async()

        while rclpy.ok():
            rclpy.spin_until_future_complete(
                self.node,
                result_future,
                timeout_sec=0.2
            )

            if result_future.done():
                result = result_future.result()
                return result.status == GoalStatus.STATUS_SUCCEEDED

        return False

    # waypoint (x, y, yaw) を PoseStamped に変換する
    def _make_pose(self, waypoint):
        x, y, yaw = waypoint

        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.node.get_clock().now().to_msg()

        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        quat = tf_transformations.quaternion_from_euler(0.0, 0.0, float(yaw))

        pose.pose.orientation.x = quat[1]
        pose.pose.orientation.y = quat[2]
        pose.pose.orientation.z = quat[3]
        pose.pose.orientation.w = quat[0]

        return pose