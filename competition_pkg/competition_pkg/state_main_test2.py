#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import Twist

from yasmin import State, StateMachine, Blackboard
from yasmin_viewer import YasminViewerPub

from competition_pkg.states.wait4start import Wait4startState  # 変更
from competition_pkg.states.of_recog import ObRecogState


class TestSmNode(Node):
    def __init__(self):
        super().__init__("state_main_test2")
        self.get_logger().info("テスト用ステートマシン起動")

        sm = StateMachine(outcomes=["EXIT"])

        # startステート
        sm.add_state(
            name="start",
            state=Wait4startState(node=self),  # 変更
            transitions={
                "success": "of-recog",
            },
        )

        # of-recogステート
        sm.add_state(
            name="of-recog",
            state=ObRecogState(node=self),
            transitions={
                "success": "EXIT",
                "failure": "start",
            },
        )

        YasminViewerPub(fsm_name="STATE_MAIN_TEST2", fsm=sm)

        outcome = sm()
        self.get_logger().info(f"ステートマシン終了: {outcome}")


def shutdown(node: Node):
    node.get_logger().info("Shutdown!!")
    pub = node.create_publisher(Twist, "cmd_vel", 10)
    pub.publish(Twist())
    node.get_clock().sleep_for(Duration(nanoseconds=100))
    node.destroy_publisher(pub)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = TestSmNode()
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            shutdown(node)
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()