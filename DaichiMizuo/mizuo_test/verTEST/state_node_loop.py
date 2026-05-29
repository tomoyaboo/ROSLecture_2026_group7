#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import rclpy
from rclpy.node import Node

from yasmin import Blackboard
from yasmin import State
from yasmin import StateMachine
from yasmin_viewer import YasminViewerPub

from ament_index_python.packages import get_package_share_directory

from .state_search.search_state import SearchState

#---------------------------------------------
#   仮の物体検知ステート。
#   実際には of-recog ステートに置き換える。
#---------------------------------------------
class ObjectRecognitionDummy(State):

    def __init__(self, node: Node):
        super().__init__(outcomes=["found", "not_found"])
        self.node = node

    def execute(self, blackboard: Blackboard) -> str:
        self.node.get_logger().info("Executing state OF_RECOG dummy")


        # 物体を見つけた場合: return "found"
        # 見つからなかった場合: return "not_found"
        return "not_found"


class SearchNode(Node):
    def __init__(self):
        super().__init__("search")

        self.declare_parameter("map_yaml", "map.yaml") #絶対パス指定に変更
        map_yaml = self.get_parameter("map_yaml").value

        if not os.path.isabs(map_yaml):
            pkg_share = get_package_share_directory("ROSLecture_2026_group7")
            map_yaml = os.path.join(pkg_share, "map", map_yaml)

        sm = StateMachine(outcomes=["FOUND", "FAILED"])

        sm.add_state(
            name="SEARCH",
            state=SearchState(self, map_yaml),
            transitions={
                "detect": "OF_RECOG",
                "loop": "SEARCH",
                "failed": "FAILED",
            },
        )

        sm.add_state(
            name="OF_RECOG",
            state=ObjectRecognitionDummy(self),
            transitions={
                "found": "FOUND",
                "not_found": "SEARCH",
            },
        )

        YasminViewerPub(fsm_name="SEARCH_STATE_MACHINE", fsm=sm)

        blackboard = Blackboard()

        outcome = sm(blackboard=blackboard)

        self.get_logger().info(f"Search state machine finished: {outcome}")


def main(args=None):
    rclpy.init(args=args)

    node = SearchNode()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()